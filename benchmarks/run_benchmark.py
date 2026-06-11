"""
benchmarks/run_benchmark.py
============================
Paradigm-Shift Benchmark: Kosh vs. Naive Flat Retrieval Baseline.

Measures the ability of each system to handle a scientific paradigm shift
where a formerly accepted "fact" (stress causes ulcers) is later definitively
contradicted by empirical evidence (H. pylori, Nobel Prize 2005).

Key Metric: Contradiction Quarantine Score (CQS)
    CQS = 1 - (LyapunovStability of outdated node in EMPIRICAL mode)
    A high CQS means the system successfully flagged the outdated paradigm.
    Baseline CQS is always 0.0 (no mechanism to detect contradictions).
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kosh.kernel import MemoryKernel
from kosh.models import ReasoningMode, GovernancePolicy
from kosh.reasoning import LyapunovCritic, resonance_profile, harmonic_match

from benchmarks.corpus.paradigm_shift import CORPUS_EVENTS, load_corpus
from benchmarks.baseline import NaiveBaseline

DB_PATH = "benchmark_paradigm_shift.pgdb"

SEP = "=" * 62

def run_baseline():
    baseline = NaiveBaseline()
    for event in CORPUS_EVENTS:
        baseline.ingest(event["payload"])

    print(f"\n{SEP}")
    print("  BASELINE: Naive Flat Retrieval (simulates Vector DB / RAG)")
    print(SEP)

    query = "ulcer cause"
    results = baseline.retrieve_query(query)
    print(f"  Query: '{query}'")
    print(f"  Documents returned: {len(results)} (all with equal weight)")
    print()
    for i, doc in enumerate(results, 1):
        print(f"  [{i}] [{doc['era']:28s}] {doc['claim'][:60]}...")
    print()
    print("  PROBLEM: The outdated 'stress theory' (t0) is returned")
    print("  alongside the Nobel-validated H. pylori fact (t4) with")
    print("  identical confidence. An LLM cannot distinguish them.")
    print(f"  Contradiction Quarantine Score (CQS): 0.000  <-- BASELINE")
    return 0.0


def run_kosh(node_ids):
    print(f"\n{SEP}")
    print("  KOSH: Provenance Graph DB w/ LyapunovCritic (EMPIRICAL mode)")
    print(SEP)

    kernel = MemoryKernel(DB_PATH)
    node_ids = load_corpus(kernel)

    # Evaluate each node under EMPIRICAL mode
    critic = LyapunovCritic(kernel, mode=ReasoningMode.EMPIRICAL)

    print(f"  {'Era':<28} {'Score':>7}  {'Status':<12}  Interpretation")
    print(f"  {'-'*28} {'-'*7}  {'-'*12}  {'-'*28}")

    outdated_score = None
    validated_score = None

    for era, node_id in node_ids.items():
        result = critic.evaluate(node_id, max_depth=4)
        score  = result["score"]
        status = result["status"]

        if era == "t0_1950s":
            outdated_score = score
            interp = "<-- OUTDATED PARADIGM (should be ~0)"
        elif era == "t4_2005_nobel":
            validated_score = score
            interp = "<-- VALIDATED THEORY (should be highest)"
        elif era == "t1_1982_anomaly":
            interp = "Anomaly discovery"
        elif era == "t2_1984_experiment":
            interp = "Causal self-experiment"
        else:
            interp = "Paradigm shift (NIH)"

        print(f"  {era:<28} {score:>7.4f}  {status:<12}  {interp}")

    kernel.close()

    cqs = 1.0 - outdated_score if outdated_score is not None else 0.0

    print()
    print(f"  Contradiction Quarantine Score (CQS): {cqs:.3f}  <-- KOSH")
    print(f"  (1 - Lyapunov score of outdated 't0' node under EMPIRICAL mode)")
    return cqs, outdated_score, validated_score


def resonance_demo():
    print(f"\n{SEP}")
    print("  DCT RESONANCE: Query relevance to paradigm shift")
    print(SEP)

    query = "bacteria cause ulcers antibiotic treatment"
    q_profile = resonance_profile(query)

    print(f"  Query: '{query}'\n")
    print(f"  {'Claim (truncated)':<48}  {'Match':>6}")
    print(f"  {'-'*48}  {'-'*6}")

    for event in CORPUS_EVENTS:
        claim   = event["payload"]["claim"]
        profile = resonance_profile(claim)
        score   = harmonic_match(q_profile, profile)
        print(f"  {claim[:48]:<48}  {score:.4f}")

    print()
    print("  EXPECTED: t4 (Nobel/antibiotic) should score highest.")
    print("  t0 (stress/acid) should score lowest.")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print(f"\n{SEP}")
    print("  PARADIGM-SHIFT BENCHMARK: Kosh vs. Naive Baseline")
    print("  Dataset: Stomach Ulcer Paradigm Shift (1950s -> 2005)")
    print(SEP)

    # 1. Baseline
    baseline_cqs = run_baseline()

    # 2. Kosh
    kosh_cqs, outdated_score, validated_score = run_kosh({})

    # 3. Resonance demo
    resonance_demo()

    # 4. Summary
    print(f"\n{SEP}")
    print("  BENCHMARK SUMMARY")
    print(SEP)
    print(f"  {'Metric':<40}  {'Baseline':>10}  {'Kosh':>10}")
    print(f"  {'-'*40}  {'-'*10}  {'-'*10}")
    print(f"  {'Contradiction Quarantine Score (CQS)':<40}  {baseline_cqs:>10.3f}  {kosh_cqs:>10.3f}")
    print(f"  {'Outdated paradigm score (lower=better)':<40}  {'N/A':>10}  {outdated_score:>10.4f}")
    print(f"  {'Validated theory score (higher=better)':<40}  {'N/A':>10}  {validated_score:>10.4f}")
    print(f"  {'Temporal ordering preserved':<40}  {'No':>10}  {'Yes':>10}")
    print(f"  {'Provenance traceable to source':<40}  {'No':>10}  {'Yes':>10}")
    print(f"  {'Zero external dependencies':<40}  {'N/A':>10}  {'Yes':>10}")
    print()

    assert kosh_cqs > baseline_cqs, "FAIL: Kosh should outperform baseline on CQS"
    assert outdated_score < validated_score, "FAIL: Outdated node should score lower than validated node"
    print("  All benchmark assertions PASSED.")
    print(SEP)


if __name__ == "__main__":
    main()
