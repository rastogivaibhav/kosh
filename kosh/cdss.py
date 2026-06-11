"""
app/kosh/cdss.py
=================
Cross-Domain Synthesis Score (CDSS)

Measures whether a node is the convergence point of multiple independent,
orthogonal research domains — each of which may have internally failed and
recovered before contributing to the synthesis.

Key insight: a node reached by 4 independent domain chains that each resolved
their own internal contradictions is MORE trustworthy, not less. This is the
inverse of within-domain contradiction scoring used by LyapunovCritic.

Mathematical definition
-----------------------
For a candidate synthesis node S with full lineage L:

    CDSS(S) = Σ domain_resolution_score(d) / |domains_seen|

    domain_resolution_score(d) =
        0.0  — domain d has no evidence nodes in lineage (not contributing)
        0.5  — domain d has Observed/Discovered nodes but no internal contradiction
        1.0  — domain d has BOTH internal contradictions AND a later resolution
               (maximum confidence: the domain worked through its own failures)

    Normalised CDSS ∈ [0, 1]

    Orthogonality bonus: if domains are semantically distinct (detected via DCT
    profile dissimilarity), CDSS is boosted by up to 0.2 to reward truly
    independent convergence lines.

Why this differs from LyapunovCritic
-------------------------------------
LyapunovCritic penalises Contradicted edges.
CDSS rewards them when they appear WITHIN a domain chain that later resolved.
The two scores are complementary:
  - Use LyapunovCritic to quarantine nodes reached by a single contradicted chain
    (linear paradigm shifts, outdated facts).
  - Use CDSS to promote nodes reached by multiple domain chains that each overcame
    their own contradictions (cross-domain consilience breakthroughs).
"""

from .kernel import MemoryKernel
from .reasoning import resonance_profile, harmonic_match


# ── Domain Resolution Scoring Constants ───────────────────────────────────────
SCORE_NO_CONTRIBUTION   = 0.0
SCORE_SIMPLE_EVIDENCE   = 0.5   # domain contributed evidence but had no internal contradictions
SCORE_RESOLVED_CONFLICT = 1.0   # domain had internal contradictions AND resolved them

ORTHOGONALITY_BONUS_MAX = 0.2   # up to 20% boost for semantically distinct domains


# ── Core CDSS Function ────────────────────────────────────────────────────────

def cross_domain_synthesis_score(synthesis_node_id: int,
                                  kernel: MemoryKernel,
                                  max_depth: int = 8) -> dict:
    """
    Compute the Cross-Domain Synthesis Score for a candidate synthesis node.

    Parameters
    ----------
    synthesis_node_id : int
        The lattice node ID of the candidate synthesis/convergence node.
    kernel : MemoryKernel
        An open Kosh MemoryKernel instance.
    max_depth : int
        How many hops back through the lineage to trace (default 8 to cover
        multi-decade research chains).

    Returns
    -------
    dict with keys:
        cdss              : float  — normalised score [0, 1]
        contributing_domains : list — domain names that contributed
        domain_scores     : dict  — per-domain resolution score
        orthogonality_bonus : float — bonus for domain semantic diversity
        breakdown         : dict  — detailed per-domain analysis
    """
    lineage = kernel.trace_lineage(synthesis_node_id, max_depth=max_depth)
    nodes   = lineage.get("nodes", {})
    edges   = lineage.get("edges", {})

    if not nodes:
        return {"cdss": 0.0, "contributing_domains": [], "domain_scores": {},
                "orthogonality_bonus": 0.0, "breakdown": {}}

    # ── Step 1: Group nodes by domain ─────────────────────────────────────────
    domain_nodes: dict[str, list] = {}   # domain → [node_id, ...]
    for node_id, node_data in nodes.items():
        payload = node_data.get("payload", {})
        domain  = payload.get("domain", "unknown")
        if domain == "synthesis":
            continue  # don't count the synthesis node itself
        domain_nodes.setdefault(domain, []).append((node_id, node_data))

    if not domain_nodes:
        return {"cdss": 0.0, "contributing_domains": [], "domain_scores": {},
                "orthogonality_bonus": 0.0, "breakdown": {}}

    # Build a quick edge lookup: target_node_id → list of edge dicts
    edges_by_target: dict[int, list] = {}
    for edge in edges:
        target = edge.get("target")
        edges_by_target.setdefault(target, []).append(edge)

    # ── Step 2: Score each domain ─────────────────────────────────────────────
    domain_scores: dict[str, float] = {}
    breakdown:     dict[str, dict]  = {}

    for domain, domain_node_list in domain_nodes.items():
        max_contradiction_ns = -1
        max_resolution_ns    = -1
        node_count           = len(domain_node_list)

        for node_id, node_data in domain_node_list:
            incoming = edges_by_target.get(int(node_id), [])
            tgt_ts = node_data.get("documented_at_ns", 0)
            for edge in incoming:
                prov = edge.get("provenance", "")
                src_id = edge.get("source")
                src_node = nodes.get(str(src_id), {}) # nodes keys are strings in JSON from trace_lineage
                if not src_node:
                    src_node = nodes.get(int(src_id), {})
                src_ts = src_node.get("documented_at_ns", 0)
                
                edge_ts = max(src_ts, tgt_ts)
                
                if "Contradicted" in prov:
                    max_contradiction_ns = max(max_contradiction_ns, edge_ts)
                if "Discovered" in prov or "Observed" in prov:
                    max_resolution_ns = max(max_resolution_ns, edge_ts)

        has_contradiction = max_contradiction_ns > -1
        has_resolution    = max_resolution_ns > -1

        if has_contradiction and has_resolution:
            if max_resolution_ns >= max_contradiction_ns:
                score = SCORE_RESOLVED_CONFLICT
                reason = "domain overcame internal contradictions (resolution supersedes or matches contradiction)"
            else:
                # Civil War: contradiction is newer than the resolution
                score = 0.2
                reason = "domain is in active conflict (contradiction supersedes resolution)"
        elif node_count > 0:
            score = SCORE_SIMPLE_EVIDENCE
            reason = "domain contributed evidence (no internal contradiction recorded)"
        else:
            score = SCORE_NO_CONTRIBUTION
            reason = "no evidence from domain found in lineage"

        domain_scores[domain] = score
        breakdown[domain] = {
            "score":              score,
            "node_count":         node_count,
            "has_contradiction":  has_contradiction,
            "has_resolution":     has_resolution,
            "reason":             reason,
        }

    # ── Step 3: Orthogonality bonus ───────────────────────────────────────────
    # Measure how semantically different the domain evidence pools are.
    # If they're all talking about the same thing, the convergence is less impressive.
    orthogonality_bonus = 0.0
    if len(domain_nodes) >= 2:
        domain_profiles = {}
        for domain, domain_node_list in domain_nodes.items():
            combined_text = " ".join(
                node_data.get("payload", {}).get("claim", "")
                for _, node_data in domain_node_list
            )
            domain_profiles[domain] = resonance_profile(combined_text)

        domain_names  = list(domain_profiles.keys())
        pair_count    = 0
        total_dissim  = 0.0

        for i in range(len(domain_names)):
            for j in range(i + 1, len(domain_names)):
                sim = harmonic_match(
                    domain_profiles[domain_names[i]],
                    domain_profiles[domain_names[j]]
                )
                total_dissim += (1.0 - sim)
                pair_count   += 1

        if pair_count > 0:
            avg_dissimilarity   = total_dissim / pair_count
            orthogonality_bonus = round(avg_dissimilarity * ORTHOGONALITY_BONUS_MAX, 4)

    # ── Step 4: Compute raw CDSS ──────────────────────────────────────────────
    contributing_domains = [d for d, s in domain_scores.items() if s > 0]
    raw_cdss = (
        sum(domain_scores.values()) / max(1, len(domain_nodes))
    ) if domain_nodes else 0.0

    final_cdss = min(1.0, raw_cdss + orthogonality_bonus)

    return {
        "cdss":                round(final_cdss, 4),
        "raw_cdss":            round(raw_cdss, 4),
        "contributing_domains":contributing_domains,
        "domain_count":        len(domain_nodes),
        "domain_scores":       domain_scores,
        "orthogonality_bonus": orthogonality_bonus,
        "breakdown":           breakdown,
    }
