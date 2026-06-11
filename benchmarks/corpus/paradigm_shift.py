"""
benchmarks/corpus/paradigm_shift.py
=====================================
Loads the "Stomach Ulcer Paradigm Shift" corpus into a Kosh MemoryKernel.

Timeline:
  t0 (1950s): Stress/diet theory is "Observed" medical consensus.
  t1 (1982):  Marshall & Warren discover H. pylori in ulcer patients (Anomaly).
  t2 (1984):  Marshall drinks H. pylori culture, develops gastritis (Causal proof).
  t3 (1994):  NIH declares H. pylori is primary cause. Old theory becomes Contradicted.
  t4 (2005):  Nobel Prize. Antibiotic treatment validated as cure.

The test:
  A naive retrieval baseline (dict store) returns ALL facts equally across time.
  Kosh's LyapunovCritic in EMPIRICAL mode should assign a near-zero stability score
  to the OLD "stress theory" node, quarantining it without explicit deletion.
"""

import time

# Use nanosecond offsets to simulate real timeline spacing
_YEAR_NS = 365 * 24 * 60 * 60 * 1_000_000_000

CORPUS_EVENTS = [
    {
        "era": "t0_1950s",
        "year_offset_ns": 0,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "claim": "Stomach ulcers are caused by stress, spicy food, and excess stomach acid.",
            "source": "Medical consensus pre-1980",
            "status": "accepted",
            "era": "t0_1950s",
        }
    },
    {
        "era": "t1_1982_anomaly",
        "year_offset_ns": 30 * _YEAR_NS,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "claim": "Marshall and Warren isolate Helicobacter pylori from ulcer biopsies.",
            "source": "Marshall & Warren, 1982",
            "status": "anomaly",
            "era": "t1_1982_anomaly",
        }
    },
    {
        "era": "t2_1984_experiment",
        "year_offset_ns": 32 * _YEAR_NS,
        "edge_origin": "Observed",
        "edge_role": "Causal",
        "payload": {
            "claim": "Marshall self-administers H. pylori culture and develops acute gastritis within days.",
            "source": "Marshall self-experiment, 1984",
            "status": "causal_proof",
            "era": "t2_1984_experiment",
        }
    },
    {
        "era": "t3_1994_paradigm_shift",
        "year_offset_ns": 42 * _YEAR_NS,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "claim": "NIH Consensus: H. pylori is the primary cause of peptic ulcers. Stress theory is invalid.",
            "source": "NIH Consensus Statement, 1994",
            "status": "paradigm_shift",
            "era": "t3_1994_paradigm_shift",
        }
    },
    {
        "era": "t4_2005_nobel",
        "year_offset_ns": 53 * _YEAR_NS,
        "edge_origin": "Observed",
        "edge_role": "Causal",
        "payload": {
            "claim": "Nobel Prize in Medicine awarded to Marshall & Warren. Antibiotic triple therapy cures peptic ulcers.",
            "source": "Nobel Committee, 2005",
            "status": "validated",
            "era": "t4_2005_nobel",
        }
    },
]


def load_corpus(kernel):
    """Ingest the paradigm-shift corpus into the MemoryKernel. Returns node_ids keyed by era."""
    now_ns = time.time_ns()
    node_ids = {}
    prev_id = None

    for event in CORPUS_EVENTS:
        ts = now_ns + event["year_offset_ns"]
        node_id = kernel.insert_node(
            event_type=1,
            payload=event["payload"],
            parent_id=prev_id,
            edge_origin=event["edge_origin"],
            edge_role=event["edge_role"],
            documented_at_ns=ts,
            valid_from_ns=ts,
        )
        node_ids[event["era"]] = node_id
        prev_id = node_id

    # Explicitly mark the old stress theory with a Contradictory edge FROM the NIH finding
    # This models the paradigm shift: t3 contradicts t0
    kernel.insert_edge(
        source_id=node_ids["t3_1994_paradigm_shift"],
        target_id=node_ids["t0_1950s"],
        edge_type=99,  # 99 = Contradiction event type
        edge_origin="Discovered",
        edge_role="Mechanistic"
    )

    return node_ids
