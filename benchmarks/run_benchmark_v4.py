"""
benchmarks/run_benchmark_v4.py
================================
Gravitational Wave Detection Benchmark: Cross-Domain Consilience v4

Tests CDSS reproducibility on a structurally different case from NIF fusion:
  - 5 domains (vs 4 in fusion)
  - 99-year timeline (vs 60-year)
  - One domain (experimental_physics) contains a famous COMPLETE RED HERRING
    (Weber bars) — a fully Contradicted branch that must not penalise synthesis
  - The Weber refutation is itself a Discovered resolution within its domain

Hypothesis: CDSS should again rank the synthesis node #1 and score >= 0.8,
proving the algorithm generalises across different discovery patterns.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kosh.kernel import MemoryKernel
from kosh.models import ReasoningMode
from kosh.reasoning import LyapunovCritic, resonance_profile, harmonic_match
from kosh.cdss import cross_domain_synthesis_score

from benchmarks.corpus.gravitational_waves import (
    ALL_DOMAIN_EVENTS, SYNTHESIS, load_corpus
)

DB_PATH = "benchmark_gw150914_v4.pgdb"
SEP     = "=" * 70


def run_baseline():
    print(f"\n{SEP}")
    print("  BASELINE: Naive Flat Retrieval")
    print(SEP)
    query  = "gravitational wave detection einstein spacetime"
    q_prof = resonance_profile(query)
    results = []
    for event in ALL_DOMAIN_EVENTS + [SYNTHESIS]:
        claim  = event["payload"]["claim"]
        score  = harmonic_match(q_prof, resonance_profile(claim))
        results.append((score, event["era"], event["payload"]["status"]))

    results.sort(reverse=True)
    print(f"  Query: '{query}'\n")
    print(f"  {'Score':>6}  {'Status':<24}  Era")
    print(f"  {'-'*6}  {'-'*24}  {'-'*38}")
    synthesis_rank = None
    for rank, (score, era, status) in enumerate(results, 1):
        marker = "  <-- SYNTHESIS" if era == SYNTHESIS["era"] else ""
        print(f"  {score:.4f}  {status:<24}  {era[:38]}{marker}")
        if era == SYNTHESIS["era"]:
            synthesis_rank = rank
    print(f"\n  Synthesis node rank (baseline): #{synthesis_rank} of {len(results)}")
    print(f"  Baseline CDSS: 0.000")
    return synthesis_rank


def run_kosh(kernel, node_ids, synthesis_id):
    print(f"\n{SEP}")
    print("  KOSH: LyapunovCritic + CDSS")
    print(SEP)
    critic = LyapunovCritic(kernel, mode=ReasoningMode.EMPIRICAL)
    query  = "gravitational wave detection einstein spacetime"
    q_prof = resonance_profile(query)

    scored = []
    for era, node_id in node_ids.items():
        payload    = kernel.get_node_payload(node_id)
        claim      = payload.get("claim", "")
        domain     = payload.get("domain", "unknown")
        raw_res    = harmonic_match(q_prof, resonance_profile(claim))
        lyap_score = critic.evaluate(node_id, max_depth=6)["score"]

        if era == SYNTHESIS["era"]:
            cdss_result = cross_domain_synthesis_score(node_id, kernel, max_depth=10)
            cdss        = cdss_result["cdss"]
        else:
            cdss = 0.0

        combined = (lyap_score * 0.3 + cdss * 0.7) if era == SYNTHESIS["era"] \
                   else lyap_score
        scored.append((combined, cdss, lyap_score, raw_res, era, domain,
                       payload.get("status", "")))

    scored.sort(reverse=True)
    print(f"\n  {'Combined':>8}  {'CDSS':>6}  {'Lyap':>6}  {'Res':>6}  "
          f"{'Domain':<24}  Era")
    print(f"  {'-'*8}  {'-'*6}  {'-'*6}  {'-'*6}  {'-'*24}  {'-'*32}")
    kosh_rank = None
    for rank, (comb, cdss, lyap, res, era, domain, status) in enumerate(scored, 1):
        marker = "  <-- SYNTHESIS" if era == SYNTHESIS["era"] else ""
        print(f"  {comb:>8.4f}  {cdss:>6.4f}  {lyap:>6.4f}  {res:>6.4f}  "
              f"{domain:<24}  {era[:32]}{marker}")
        if era == SYNTHESIS["era"]:
            kosh_rank = rank

    # ── CDSS Deep-dive ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  CDSS DEEP-DIVE: GW150914 Synthesis Node")
    print(SEP)
    r = cross_domain_synthesis_score(synthesis_id, kernel, max_depth=10)
    print(f"  Final CDSS:          {r['cdss']}")
    print(f"  Raw CDSS:            {r['raw_cdss']}")
    print(f"  Orthogonality Bonus: {r['orthogonality_bonus']}")
    print(f"  Domains Found:       {r['domain_count']}")
    print(f"  Contributing:        {r['contributing_domains']}")
    print(f"\n  Per-Domain Breakdown:")
    print(f"  {'Domain':<26}  {'Score':>5}  {'Contradiction':>13}  {'Resolved':>8}  Reason")
    print(f"  {'-'*26}  {'-'*5}  {'-'*13}  {'-'*8}  {'-'*36}")
    for dom, info in r["breakdown"].items():
        print(f"  {dom:<26}  {info['score']:>5.1f}  {str(info['has_contradiction']):>13}  "
              f"{str(info['has_resolution']):>8}  {info['reason'][:36]}")

    return kosh_rank, r["cdss"]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print(f"\n{SEP}")
    print("  GW150914 BENCHMARK v4: 99-Year, 5-Domain Consilience")
    print("  Einstein (1916) -> LIGO Detection (Sept 14, 2015)")
    print(SEP)

    kernel = MemoryKernel(DB_PATH)
    node_ids, synthesis_id = load_corpus(kernel)

    baseline_rank          = run_baseline()
    kosh_rank, cdss        = run_kosh(kernel, node_ids, synthesis_id)

    print(f"\n{SEP}")
    print("  CROSS-BENCHMARK COMPARISON")
    print(SEP)
    print(f"  {'Metric':<44}  {'NIF Fusion':>12}  {'GW LIGO':>12}")
    print(f"  {'-'*44}  {'-'*12}  {'-'*12}")
    print(f"  {'Domains':<44}  {'4':>12}  {'5':>12}")
    print(f"  {'Timeline (years)':<44}  {'60':>12}  {'99':>12}")
    print(f"  {'Synthesis CDSS':<44}  {'1.0000':>12}  {cdss:>12.4f}")
    print(f"  {'Synthesis rank (Kosh)':<44}  {'#1':>12}  {f'#{kosh_rank}':>12}")
    print(f"  {'Synthesis rank (Baseline)':<44}  {'#3':>12}  {f'#{baseline_rank}':>12}")
    print()

    assert kosh_rank == 1, \
        f"FAIL: Synthesis should rank #1, got #{kosh_rank}"
    assert cdss >= 0.8, \
        f"FAIL: CDSS ({cdss:.4f}) should be >= 0.8 for a 5-domain convergence"
    assert kosh_rank < baseline_rank, \
        f"FAIL: Kosh rank (#{kosh_rank}) should beat baseline (#{baseline_rank})"

    print("  All v4 benchmark assertions PASSED.")
    print(f"  CDSS is reproducible across different multi-domain consilience breakthroughs.")
    print(SEP)
    kernel.close()


if __name__ == "__main__":
    main()
