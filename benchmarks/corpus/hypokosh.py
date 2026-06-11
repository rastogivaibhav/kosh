"""
benchmarks/corpus/hypokosh.py
==========================================
Hypokosh Synthesis Corpus — Agentic Database Architecture

Can CDSS independently derive our own "Hypokosh" architecture from 
foundational literature across diverse AI and cognitive science domains?

Domain A — LLM Reasoning (ReAct, Generative Agents, Self-RAG)
Domain B — Retrieval Architectures (Attention, RAG)
Domain C — Cognitive Architectures (SOAR, ACT-R)
Domain D — Plausible & Causal Reasoning (Pearl, Polya)

Each domain has internal progression and limitations (contradictions).
The synthesis node (Hypokosh) unites them: a local-first, memory-mapped
agentic database with cognitive plasticity, contradiction-aware scoring,
and spatial graphene lattice memory.
"""

import time

_YEAR_NS = 365 * 24 * 60 * 60 * 1_000_000_000
# Synthetic epoch so that year=-68 is still strongly positive
_BASE_NS = 100 * _YEAR_NS

def _ts(year_offset):
    return _BASE_NS + year_offset * _YEAR_NS

# ── Domain A: LLM Reasoning ──────────────────────────────────────────────────
DOMAIN_A = [
    {
        "domain": "llm_reasoning",
        "era": "react_2022",
        "year": 0,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "llm_reasoning",
            "claim": "ReAct (Yao et al.): Synergizing Reasoning and Acting in LMs. Models can interleave thoughts and actions.",
            "source": "arXiv:2210.03629",
            "status": "foundation",
            "era": "react_2022",
        }
    },
    {
        "domain": "llm_reasoning",
        "era": "generative_agents_2023",
        "year": 1,
        "edge_origin": "Hypothetical",
        "edge_role": "Predictive",
        "payload": {
            "domain": "llm_reasoning",
            "claim": "Generative Agents (Park et al.): Agents can reflect, plan, and remember, but memory streams grow unbounded and lack rigorous contradiction resolution.",
            "source": "arXiv:2304.03442",
            "status": "failure", # Limitation: unbounded memory, no contradiction resolution
            "era": "generative_agents_2023",
        }
    },
    {
        "domain": "llm_reasoning",
        "era": "self_rag_2023",
        "year": 2,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "llm_reasoning",
            "claim": "Self-RAG (Asai et al.): Learning to retrieve, generate, and critique through self-reflection. Introduces critique tokens to resolve generation contradictions.",
            "source": "arXiv:2310.11511",
            "status": "resolved",
            "era": "self_rag_2023",
        }
    },
]

# ── Domain B: Retrieval Architectures ─────────────────────────────────────────
DOMAIN_B = [
    {
        "domain": "retrieval_architectures",
        "era": "attention_2017",
        "year": -5,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "retrieval_architectures",
            "claim": "Attention Is All You Need (Vaswani et al.): Transformers learn contextual representations, but context window is finite.",
            "source": "arXiv:1706.03762",
            "status": "foundation",
            "era": "attention_2017",
        }
    },
    {
        "domain": "retrieval_architectures",
        "era": "rag_2020",
        "year": -2,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "retrieval_architectures",
            "claim": "RAG (Lewis et al.): Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Naive vector DBs retrieve flat chunks regardless of temporal validity or contradiction.",
            "source": "arXiv:2005.11401",
            "status": "failure", # Limitation: flat retrieval, temporal blindness
            "era": "rag_2020",
        }
    },
    {
        "domain": "retrieval_architectures",
        "era": "temporal_graphs_2024",
        "year": 3,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "retrieval_architectures",
            "claim": "Graph-RAG approaches: Storing knowledge as causal graphs rather than flat chunks allows topological analysis of knowledge provenance.",
            "source": "Community Consensus 2024",
            "status": "resolved",
            "era": "temporal_graphs_2024",
        }
    },
]

# ── Domain C: Cognitive Architectures ─────────────────────────────────────────
DOMAIN_C = [
    {
        "domain": "cognitive_architectures",
        "era": "soar_1987",
        "year": -35,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "cognitive_architectures",
            "claim": "SOAR (Laird, Newell, Rosenbloom): An Architecture for General Intelligence. Symbolic representation of state spaces and operators.",
            "source": "Artificial Intelligence, 1987",
            "status": "foundation",
            "era": "soar_1987",
        }
    },
    {
        "domain": "cognitive_architectures",
        "era": "act_r_1993",
        "year": -29,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "cognitive_architectures",
            "claim": "ACT-R (Anderson): The Architecture of Cognition. Models human memory decay and activation. But entirely rigid, brittle, non-differentiable symbolic structures.",
            "source": "Harvard University Press",
            "status": "failure", # Limitation: rigid symbolic structures, lacks fuzzy embedding logic
            "era": "act_r_1993",
        }
    },
    {
        "domain": "cognitive_architectures",
        "era": "neurosymbolic_2025",
        "year": 4,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "cognitive_architectures",
            "claim": "Neurosymbolic systems blend ACT-R's cognitive plasticity (habituation, pruning) with continuous embedding spaces.",
            "source": "Synthesis trend",
            "status": "resolved",
            "era": "neurosymbolic_2025",
        }
    },
]

# ── Domain D: Plausible & Causal Reasoning ────────────────────────────────────
DOMAIN_D = [
    {
        "domain": "causal_reasoning",
        "era": "polya_1954",
        "year": -68,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "causal_reasoning",
            "claim": "Pólya: Mathematics and Plausible Reasoning. Heuristic reasoning, inference, and discovering truth via plausible patterns.",
            "source": "Princeton University Press",
            "status": "foundation",
            "era": "polya_1954",
        }
    },
    {
        "domain": "causal_reasoning",
        "era": "pearl_2000",
        "year": -22,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "causal_reasoning",
            "claim": "Pearl: Causality. Causal diagrams (DAGs) and do-calculus. Requires explicitly mapped causal graphs, fails on unstructured natural language.",
            "source": "Cambridge University Press",
            "status": "failure", # Limitation: requires manual rigid DAGs
            "era": "pearl_2000",
        }
    },
    {
        "domain": "causal_reasoning",
        "era": "lyapunov_stability_2026",
        "year": 5,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "causal_reasoning",
            "claim": "Lyapunov Stability on Knowledge Graphs: Causal validity can be dynamically computed by evaluating contradiction weight and temporal consistency across pathways.",
            "source": "Novel Graph Theorem",
            "status": "resolved",
            "era": "lyapunov_stability_2026",
        }
    },
]

# ── Synthesis Node ────────────────────────────────────────────────────────────
SYNTHESIS = {
    "domain": "synthesis",
    "era": "hypokosh_2026",
    "year": 6,
    "payload": {
        "domain": "synthesis",
        "claim": "Hypokosh (2026): A local-first, memory-mapped agentic database using a spatial graphene lattice. Merges ACT-R plasticity, Pearl's causal DAGs, RAG embeddings, and ReAct self-reflection into a single O(1) Contradiction-Aware Retrieval graph.",
        "source": "FactorySystem v3",
        "status": "validated_breakthrough",
        "era": "hypokosh_2026",
        "domains_contributing": [
            "llm_reasoning", "retrieval_architectures",
            "cognitive_architectures", "causal_reasoning"
        ],
    }
}

ALL_DOMAINS = [DOMAIN_A, DOMAIN_B, DOMAIN_C, DOMAIN_D]
ALL_DOMAIN_EVENTS = DOMAIN_A + DOMAIN_B + DOMAIN_C + DOMAIN_D

def load_corpus(kernel):
    """
    Ingest all four domain chains and the synthesis node into Kosh.
    Returns (node_ids dict, synthesis_id int).
    """
    now_ns = _BASE_NS
    node_ids = {}

    for domain_events in ALL_DOMAINS:
        prev_id = None
        for event in domain_events:
            ts = now_ns + event["year"] * _YEAR_NS
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

    # ── Mark within-domain limitations/failures as Contradicted by resolutions ──────
    failure_pairs = {
        "llm_reasoning": ("generative_agents_2023", "self_rag_2023"),
        "retrieval_architectures": ("rag_2020", "temporal_graphs_2024"),
        "cognitive_architectures": ("act_r_1993", "neurosymbolic_2025"),
        "causal_reasoning": ("pearl_2000", "lyapunov_stability_2026"),
    }
    
    # We must ensure the resolution is timestamped STRICTLY AFTER the contradiction 
    # to pass the new Civil War check in CDSS.
    
    for domain, (failure_era, resolution_era) in failure_pairs.items():
        if failure_era in node_ids and resolution_era in node_ids:
            kernel.insert_edge(
                source_id=node_ids[resolution_era],
                target_id=node_ids[failure_era],
                edge_type=99,
                edge_origin="Contradicted",
                edge_role="Mechanistic",
            )

    # ── Synthesis node ────────────────────────────────────────────────────────
    syn_ts = now_ns + SYNTHESIS["year"] * _YEAR_NS
    synthesis_id = kernel.insert_node(
        event_type=2,
        payload=SYNTHESIS["payload"],
        parent_id=None,
        documented_at_ns=syn_ts,
        valid_from_ns=syn_ts,
    )
    node_ids[SYNTHESIS["era"]] = synthesis_id

    # ── Connect each domain's final resolved node to synthesis ────────────────
    domain_finals = {
        "llm_reasoning": "self_rag_2023",
        "retrieval_architectures": "temporal_graphs_2024",
        "cognitive_architectures": "neurosymbolic_2025",
        "causal_reasoning": "lyapunov_stability_2026",
    }
    for domain, final_era in domain_finals.items():
        if final_era in node_ids:
            kernel.insert_edge(
                source_id=node_ids[final_era],
                target_id=synthesis_id,
                edge_type=2,
                edge_origin="Observed",
                edge_role="Causal",
            )

    return node_ids, synthesis_id
