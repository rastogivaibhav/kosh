import math
import hashlib
import re
from collections import Counter
from typing import Dict, List, Optional
from .kernel import MemoryKernel
from .models import ReasoningMode, GovernancePolicy

# --- 1. Resonance Retrieval (DCT Math) ---

_N_COMPONENTS = 32

def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

def _dct(x: List[float]) -> List[float]:
    """DCT-II: standard type-II Discrete Cosine Transform"""
    N = len(x)
    if N == 0:
        return []
    result = []
    for k in range(N):
        s = sum(x[n] * math.cos(math.pi * k * (2 * n + 1) / (2 * N)) for n in range(N))
        result.append(2.0 * s)
    return result

def resonance_profile(text: str, n_components: int = _N_COMPONENTS) -> Dict[str, List[float]]:
    """Build a DCT-based resonance profile for text mapping to frequency bands."""
    tokens = tokenize(text)
    band = n_components // 3
    if not tokens:
        return {
            "low": [0.0] * band,
            "mid": [0.0] * band,
            "high": [0.0] * (n_components - 2 * band),
        }

    tf = Counter(tokens)
    total = len(tokens)
    freq_vector = [0.0] * n_components
    
    # Hash-bucket projection
    for token, cnt in tf.items():
        weight = cnt / total
        digest = int(hashlib.md5(token.encode(), usedforsecurity=False).hexdigest(), 16)
        bucket = digest % n_components
        freq_vector[bucket] += weight

    coeffs = _dct(freq_vector)
    return {
        "low": coeffs[:band],
        "mid": coeffs[band : 2 * band],
        "high": coeffs[2 * band :],
    }

def harmonic_match(profile_a: Dict[str, List[float]], profile_b: Dict[str, List[float]]) -> float:
    """Compute multi-scale resonance score between two profiles."""
    weights = {"low": 0.5, "mid": 0.3, "high": 0.2}
    score = 0.0
    
    for band, w in weights.items():
        a = profile_a.get(band, [])
        b = profile_b.get(band, [])
        if not a or not b:
            continue
        min_len = min(len(a), len(b))
        dot = sum(a[i] * b[i] for i in range(min_len))
        norm_a = math.sqrt(sum(v * v for v in a))
        norm_b = math.sqrt(sum(v * v for v in b))
        if norm_a > 0 and norm_b > 0:
            score += w * (dot / (norm_a * norm_b))
            
    return min(1.0, max(0.0, score))


# --- 2. Lyapunov Stability Critic ---

class LyapunovCritic:
    """
    Computes stability score V for a Causal Lineage Graph returned by the MemoryKernel.
    V = w1*temporal_consistency + w2*path_diversity - w3*contradiction_score
    """
    
    def __init__(self, kernel: MemoryKernel, mode: ReasoningMode = ReasoningMode.BALANCED):
        self.kernel = kernel
        self.mode = mode

        # Base weights stay fixed; contradiction penalty shifts with cognitive state
        self.weights = {
            "temporal_consistency": 0.5,
            "path_diversity": 0.3,
            "contradiction_score": self._contradiction_weight(mode)
        }

    @staticmethod
    def _contradiction_weight(mode: ReasoningMode) -> float:
        """Dynamic contradiction penalty based on cognitive state.

        Applied to Hypothetical edges.
        Contradicted edges get a separate, fixed extreme penalty (see evaluate).

        EMPIRICAL   -> High penalty (1.5): hypothetical edges are nearly disqualifying.
        THEORETICAL -> Low penalty (0.05): hypothetical edges are celebrated, not punished.
        BALANCED    -> Standard penalty (0.2): default behaviour.
        """
        return {
            ReasoningMode.EMPIRICAL:   1.5,
            ReasoningMode.THEORETICAL: 0.05,
            ReasoningMode.BALANCED:    0.2,
        }.get(mode, 0.2)

    def evaluate(self, root_node_id: int, max_depth: int = 3) -> dict:
        lineage = self.kernel.trace_lineage(root_node_id, max_depth)
        
        nodes = lineage["nodes"]
        edges = lineage["edges"]
        
        if not edges:
            return {"score": 0.0, "status": "no_evidence"}

        # 1. Temporal Consistency
        # Do causes precede effects?
        temporally_valid = 0
        for edge in edges:
            src = nodes.get(edge["source"])
            tgt = nodes.get(edge["target"])
            if src and tgt:
                if src["timestamps"]["valid_from"] <= tgt["timestamps"]["valid_from"]:
                    temporally_valid += 1
                    
        temporal_score = temporally_valid / len(edges)
        
        # 2. Path Diversity & Habituation
        # Instead of just counting edges, we sum their habituated salience.
        # This prevents self-confirmation loops from infinitely inflating the score.
        target_saliences = {}
        for edge in edges:
            target = edge["target"]
            salience = edge.get("salience", 1.0)
            target_saliences[target] = target_saliences.get(target, 0.0) + salience
            
        # Nodes with multiple inputs (meaningful path diversity)
        # We define a "diverse" node as having a combined salience > 1.5
        nodes_with_diverse_inputs = sum(1 for s in target_saliences.values() if s > 1.5)
        path_diversity = min(1.0, nodes_with_diverse_inputs / max(1, len(nodes)))
        
        # 3. Contradiction Scores (two tiers)
        # Tier A: Hypothetical edges — mode-dependent penalty
        hypothetical_salience = sum(
            e.get("salience", 1.0) for e in edges
            if "Hypothetical" in e.get("provenance", "")
        )
        # Tier B: Contradicted edges — fixed extreme penalty regardless of mode.
        # A Contradicted edge means empirical evidence has explicitly refuted this node.
        # However, if a later 'Discovered' or 'Observed' edge exists in the lineage, the contradiction is resolved.
        max_contradiction_ns = -1
        max_resolution_ns = -1
        contradicted_salience = 0.0

        for edge in edges:
            prov = edge.get("provenance", "")
            t_id = edge.get("target")
            s_id = edge.get("source")
            tgt = nodes.get(str(t_id), nodes.get(t_id, {}))
            src = nodes.get(str(s_id), nodes.get(s_id, {}))
            edge_ts = max(tgt.get("timestamps", {}).get("valid_from", 0),
                          src.get("timestamps", {}).get("valid_from", 0))
            
            if "Contradicted" in prov:
                contradicted_salience += edge.get("salience", 1.0)
                max_contradiction_ns = max(max_contradiction_ns, edge_ts)
            elif "Discovered" in prov or "Observed" in prov:
                max_resolution_ns = max(max_resolution_ns, edge_ts)

        # Only apply hard penalty if contradiction remains unresolved
        has_unresolved_contradiction = max_contradiction_ns > -1 and max_contradiction_ns > max_resolution_ns
        if not has_unresolved_contradiction:
            contradicted_salience = 0.0

        total_salience    = sum(e.get("salience", 1.0) for e in edges)
        hypothesis_score  = hypothetical_salience  / max(1.0, total_salience)
        contradiction_score = contradicted_salience / max(1.0, total_salience)

        # Fixed contradiction penalty is always 3.0 — even in THEORETICAL mode
        # a truly contradicted fact is not useful speculation, it is an error.
        CONTRADICTION_HARD_PENALTY = 3.0
        
        # V Calculation (note: contradiction weight is mode-dependent)
        w = self.weights
        # In THEORETICAL mode score formula is additive (hypotheticals are useful);
        # in EMPIRICAL mode the penalty can drive score below 0.0 before clamping.
        score = (
            w["temporal_consistency"] * temporal_score
            + w["path_diversity"] * path_diversity
            - w["contradiction_score"] * hypothesis_score
            - CONTRADICTION_HARD_PENALTY * contradiction_score
        )
        score = max(0.0, min(1.0, score))
        
        if score >= 0.7:
            status = "stable"
        elif score >= 0.4:
            status = "marginal"
        else:
            status = "unstable"
            
        return {
            "score": round(score, 4),
            "status": status,
            "mode": self.mode.value,
            "metrics": {
                "temporal_consistency":   round(temporal_score, 4),
                "path_diversity":         round(path_diversity, 4),
                "hypothesis_score":       round(hypothesis_score, 4),
                "contradiction_score":    round(contradiction_score, 4),
                "contradiction_weight":   self.weights["contradiction_score"],
                "hard_penalty_applied":   round(CONTRADICTION_HARD_PENALTY * contradiction_score, 4),
            }
        }

# --- 3. Provenance-Aware Resonance ---

def provenance_aware_resonance(query: str, node_id: int, kernel: MemoryKernel, max_depth: int = 4) -> dict:
    """
    Combines DCT harmonic match with lineage provenance state.

    Applies a heavy penalty (0.8) to the resonance score if the lineage contains
    a 'Contradicted' edge that has NOT been temporally resolved by a later
    'Discovered' or 'Observed' edge.
    """
    payload = kernel.get_node_payload(node_id)
    claim   = payload.get("claim", "")
    q_prof  = resonance_profile(query)
    c_prof  = resonance_profile(claim)
    raw     = harmonic_match(q_prof, c_prof)

    lineage  = kernel.trace_lineage(node_id, max_depth=max_depth)
    nodes    = lineage.get("nodes", {})
    edges    = lineage.get("edges", [])

    max_contradiction_ns = -1
    max_resolution_ns    = -1

    for edge in edges:
        tgt_id = edge.get("target")
        src_id = edge.get("source")
        
        tgt_node = nodes.get(str(tgt_id), nodes.get(int(tgt_id), {})) if tgt_id else {}
        src_node = nodes.get(str(src_id), nodes.get(int(src_id), {})) if src_id else {}
        
        tgt_ts = tgt_node.get("timestamps", {}).get("valid_from", 0)
        src_ts = src_node.get("timestamps", {}).get("valid_from", 0)
        edge_ts = max(src_ts, tgt_ts)
        
        prov = edge.get("provenance", "")
        if "Contradicted" in prov:
            max_contradiction_ns = max(max_contradiction_ns, edge_ts)
        elif "Discovered" in prov or "Observed" in prov:
            max_resolution_ns = max(max_resolution_ns, edge_ts)

    has_unresolved_contradiction = max_contradiction_ns > -1 and max_contradiction_ns > max_resolution_ns
    penalty   = 0.8 if has_unresolved_contradiction else 0.0
    adjusted  = max(0.0, raw - penalty)

    return {
        "raw_resonance":      round(raw, 4),
        "provenance_penalty": round(penalty, 4),
        "adjusted":           round(adjusted, 4),
        "contradicted":       has_unresolved_contradiction,
    }
