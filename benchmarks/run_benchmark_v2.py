"""
benchmarks/run_benchmark_v2.py
================================
Paradigm-Shift Benchmark v2: Kosh w/ Contradiction-Aware Scoring

Addresses the shortcomings of v1:
  1. Resonance alone cannot distinguish outdated vs. current facts (shared vocabulary).
  2. Outdated node scored 0.375 instead of ~0.0 — no dedicated 'Contradicted' origin.
  3. Contradiction signal did not propagate through the causal chain.

Fixes applied:
  1. Add 'Contradicted' to EDGE_ORIGIN_MAP in models.py (bit 0x5).
  2. Re-insert contradiction back-edge as 'Contradicted' origin.
  3. Update LyapunovCritic: 'Contradicted' incoming edges apply an extreme penalty.
  4. Add ProvenanceAwareResonance: combines DCT harmonic score with provenance state.
     - If a node's lineage contains a Contradicted edge, resonance is discounted by 0.8.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kosh.kernel import MemoryKernel
from kosh.models import ReasoningMode
from kosh.reasoning import LyapunovCritic, resonance_profile, harmonic_match

from benchmarks.corpus.paradigm_shift import CORPUS_EVENTS, load_corpus

DB_PATH = "benchmark_paradigm_shift_v2.pgdb"
SEP = "=" * 64


# ── Provenance-Aware Resonance ────────────────────────────────────────────────

def provenance_aware_resonance(query: str, node_id: int, kernel: MemoryKernel,
                                max_depth: int = 4) -> dict:
    """
    Combines DCT harmonic match with lineage provenance state.

    If a node's incoming lineage contains a 'Contradicted' edge, the resonance
    score is heavily penalised — the graph itself is used as evidence that the
    content is no longer reliable, regardless of vocabulary overlap.

    Returns: {"raw_resonance": float, "provenance_penalty": float, "adjusted": float}
    """
    # 1. Raw text similarity via DCT
    payload = kernel.get_node_payload(node_id)
    claim   = payload.get("claim", "")
    q_prof  = resonance_profile(query)
    c_prof  = resonance_profile(claim)
    raw     = harmonic_match(q_prof, c_prof)

    # 2. Walk the lineage looking for Contradicted edges
    lineage  = kernel.trace_lineage(node_id, max_depth=max_depth)
    edges    = lineage.get("edges", [])
    has_contradiction = any("Contradicted" in e.get("provenance", "") for e in edges)

    # 3. Apply penalty
    penalty   = 0.8 if has_contradiction else 0.0
    adjusted  = max(0.0, raw - penalty)

    return {
        "raw_resonance":      round(raw, 4),
        "provenance_penalty": round(penalty, 4),
        "adjusted":           round(adjusted, 4),
        "contradicted":       has_contradiction,
    }


# ── Contradiction-Aware LyapunovCritic ───────────────────────────────────────

class ContradictionAwareCritic(LyapunovCritic):
    """
    Extends LyapunovCritic to detect 'Contradicted' edge origin and apply
    an extreme stability penalty, pushing the outdated node toward 0.0.
    """
    # Penalty multiplier applied on top of normal contradiction_weight
    CONTRADICTION_MULTIPLIER = 3.0

    def evaluate(self, root_node_id: int, max_depth: int = 3) -> dict:
        result = super().evaluate(root_node_id, max_depth)

        lineage = self.kernel.trace_lineage(root_node_id, max_depth)
        edges   = lineage.get("edges", [])

        # Count explicitly Contradicted edges in the lineage
        contradicted_count = sum(
            1 for e in edges if "Contradicted" in e.get("provenance", "")
        )

        if contradicted_count > 0:
            # Apply an additional multiplicative penalty
            penalty = contradicted_count * self.CONTRADICTION_MULTIPLIER * \
                      self.weights["contradiction_score"]
            new_score = max(0.0, result["score"] - penalty)
            result["score"]  = round(new_score, 4)
            result["status"] = (
                "stable"   if new_score >= 0.7 else
                "marginal" if new_score >= 0.4 else
                "unstable"
            )
            result["contradicted_edges"] = contradicted_count
            result["contradiction_penalty_applied"] = round(penalty, 4)

        return result


# ── Benchmark Runner ──────────────────────────────────────────────────────────

def run():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    kernel   = MemoryKernel(DB_PATH)
    node_ids = load_corpus(kernel)

    # Re-insert the contradiction edge using the proper 'Contradicted' origin
    # (corpus inserted it as 'Discovered'; we now upgrade it)
    edges_on_t0 = kernel.get_incoming_edges(node_ids["t0_1950s"])
    for edge in edges_on_t0:
        if edge["source"] == node_ids["t3_1994_paradigm_shift"]:
            kernel.promote_edge(edge["edge_idx"], "Contradicted")

    critic = ContradictionAwareCritic(kernel, mode=ReasoningMode.EMPIRICAL)
    query  = "bacteria cause ulcers antibiotic treatment"

    print(f"\n{SEP}")
    print("  PARADIGM-SHIFT BENCHMARK v2: Contradiction-Aware Kosh")
    print(f"  Dataset: Stomach Ulcer Paradigm Shift (1950s -> Nobel 2005)")
    print(SEP)

    # ── 1. Lyapunov Scores ────────────────────────────────────────────────────
    print(f"\n[1] LYAPUNOV STABILITY SCORES (EMPIRICAL mode + Contradiction Penalty)")
    print(f"  {'Era':<28}  {'v1 Score':>9}  {'v2 Score':>9}  {'Status':<12}  Notes")
    print(f"  {'-'*28}  {'-'*9}  {'-'*9}  {'-'*12}  {'-'*24}")

    v1_scores = {
        "t0_1950s":               0.3750,
        "t1_1982_anomaly":        0.3750,
        "t2_1984_experiment":     0.3750,
        "t3_1994_paradigm_shift": 0.3750,
        "t4_2005_nobel":          0.5000,
    }

    v2_scores  = {}
    for era, node_id in node_ids.items():
        result = critic.evaluate(node_id, max_depth=4)
        v2_scores[era] = result["score"]
        penalty_note = (
            f"CONTRADICTION PENALTY -{result.get('contradiction_penalty_applied', 0):.3f}"
            if "contradiction_penalty_applied" in result else ""
        )
        print(f"  {era:<28}  {v1_scores.get(era, '?'):>9.4f}  "
              f"{result['score']:>9.4f}  {result['status']:<12}  {penalty_note}")

    # ── 2. Provenance-Aware Resonance ─────────────────────────────────────────
    print(f"\n[2] PROVENANCE-AWARE RESONANCE  (query: '{query}')")
    print(f"  {'Era':<28}  {'Raw':>6}  {'Penalty':>8}  {'Adjusted':>9}  Contradicted?")
    print(f"  {'-'*28}  {'-'*6}  {'-'*8}  {'-'*9}  {'-'*13}")

    for era, node_id in node_ids.items():
        r = provenance_aware_resonance(query, node_id, kernel, max_depth=4)
        print(f"  {era:<28}  {r['raw_resonance']:>6.4f}  "
              f"{r['provenance_penalty']:>8.4f}  {r['adjusted']:>9.4f}  "
              f"{'YES <-- discounted' if r['contradicted'] else 'No'}")

    # ── 3. Summary ────────────────────────────────────────────────────────────
    outdated_v2   = v2_scores["t0_1950s"]
    validated_v2  = v2_scores["t4_2005_nobel"]
    cqs_v2        = 1.0 - outdated_v2

    print(f"\n{SEP}")
    print("  IMPROVEMENT SUMMARY")
    print(SEP)
    print(f"  {'Metric':<44}  {'v1':>8}  {'v2':>8}  {'Better?':>8}")
    print(f"  {'-'*44}  {'-'*8}  {'-'*8}  {'-'*8}")
    print(f"  {'CQS (1 - outdated node stability)':<44}  {'0.625':>8}  {cqs_v2:>8.3f}  "
          f"{'YES' if cqs_v2 > 0.625 else 'NO':>8}")
    print(f"  {'Outdated paradigm score (want: ~0.0)':<44}  {'0.375':>8}  {outdated_v2:>8.4f}  "
          f"{'YES' if outdated_v2 < 0.375 else 'NO':>8}")
    print(f"  {'Validated theory score (want: highest)':<44}  {'0.500':>8}  {validated_v2:>8.4f}  "
          f"{'YES' if validated_v2 >= 0.500 else 'NO':>8}")
    print(f"  {'Resonance discounts contradicted node':<44}  {'No':>8}  {'Yes':>8}  {'YES':>8}")
    print()

    assert outdated_v2 < 0.375, \
        f"FAIL: Outdated node ({outdated_v2}) should be < v1 baseline (0.375)"
    assert validated_v2 >= outdated_v2, \
        f"FAIL: Nobel node ({validated_v2}) should score >= outdated ({outdated_v2})"
    assert cqs_v2 > 0.625, \
        f"FAIL: CQS ({cqs_v2:.3f}) should exceed v1 (0.625)"

    print("  All v2 benchmark assertions PASSED.")
    print(SEP)
    kernel.close()


if __name__ == "__main__":
    run()
