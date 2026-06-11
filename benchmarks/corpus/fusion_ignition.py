"""
benchmarks/corpus/fusion_ignition.py
======================================
NIF Fusion Ignition Corpus — Cross-Domain Consilience Dataset

Four completely independent research domains each FAILED individually over 60 years.
Their combination produced the first fusion ignition (3.15 MJ output, Dec 2022).

Domain A — Laser Physics
Domain B — Plasma Physics (Lawson Criterion / Instabilities)
Domain C — Materials Science (Capsule Engineering)
Domain D — Target Geometry (Hohlraum / Drive Symmetry)

Each domain node carries a `domain` tag so the CDSS engine can detect
cross-domain convergence vs. within-domain contradiction.

Corpus design rules:
  - Within-domain failures are marked Contradicted once resolved
  - Resolutions within a domain are marked Discovered
  - Final contributions to the synthesis are marked Observed
  - The synthesis node has no parent — all 4 domain chains insert edges to it
"""

import time

_YEAR_NS = 365 * 24 * 60 * 60 * 1_000_000_000
_BASE_NS = time.time_ns()


def _ts(year_offset):
    return _BASE_NS + year_offset * _YEAR_NS


# ── Domain A: Laser Physics ───────────────────────────────────────────────────
DOMAIN_A = [
    {
        "domain": "laser_physics",
        "era": "laser_1960_invention",
        "year": 0,
        "edge_origin": "Observed",
        "edge_role": "Causal",
        "payload": {
            "domain": "laser_physics",
            "claim": "Maiman demonstrates first ruby laser (1960). Controlled coherent light is possible.",
            "source": "Maiman, T.H. (1960). Nature.",
            "status": "foundation",
            "era": "laser_1960_invention",
        }
    },
    {
        "domain": "laser_physics",
        "era": "laser_1996_nif_design",
        "year": 36,
        "edge_origin": "Hypothetical",
        "edge_role": "Predictive",
        "payload": {
            "domain": "laser_physics",
            "claim": "NIF proposes 192-beam 1.8 MJ laser array. Sufficient energy for ignition — if delivery is uniform.",
            "source": "NIF CDR, 1994",
            "status": "hypothesis",
            "era": "laser_1996_nif_design",
        }
    },
    {
        "domain": "laser_physics",
        "era": "laser_2009_failure",
        "year": 49,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "laser_physics",
            "claim": "NIF first shot: laser delivery non-uniform, beam imbalance >3%. Implosion fails.",
            "source": "Moses, E. (2009). NIF Operations Report.",
            "status": "failure",
            "era": "laser_2009_failure",
        }
    },
    {
        "domain": "laser_physics",
        "era": "laser_2014_pulse_shaping",
        "year": 54,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "laser_physics",
            "claim": "Laser pulse shaping (picket fence + main pulse) reduces beam imbalance to <0.5%. Uniformity solved.",
            "source": "Spaeth et al. (2014). Fusion Science and Technology.",
            "status": "resolved",
            "era": "laser_2014_pulse_shaping",
        }
    },
]

# ── Domain B: Plasma Physics ──────────────────────────────────────────────────
DOMAIN_B = [
    {
        "domain": "plasma_physics",
        "era": "plasma_1957_lawson",
        "year": -3,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "plasma_physics",
            "claim": "Lawson Criterion (1957): ignition requires n*T*tau > 3x10^21 keV·s/m³. Sets the target.",
            "source": "Lawson, J.D. (1957). Proc. Phys. Soc. B.",
            "status": "foundation",
            "era": "plasma_1957_lawson",
        }
    },
    {
        "domain": "plasma_physics",
        "era": "plasma_1980_rayleigh_taylor",
        "year": 20,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "plasma_physics",
            "claim": "Rayleigh-Taylor hydrodynamic instability destroys all inertial confinement implosions. 20 years of failures.",
            "source": "Bodner (1974); multiple NRL reports 1975-1985.",
            "status": "failure",
            "era": "plasma_1980_rayleigh_taylor",
        }
    },
    {
        "domain": "plasma_physics",
        "era": "plasma_2015_hotspot_model",
        "year": 55,
        "edge_origin": "Inferred",
        "edge_role": "Predictive",
        "payload": {
            "domain": "plasma_physics",
            "claim": "Hot-spot ignition model: if central hot-spot reaches 10 keV, alpha-particle self-heating drives ignition wave. Instabilities must be suppressed only at capsule surface.",
            "source": "Hurricane et al. (2014). Nature.",
            "status": "resolved",
            "era": "plasma_2015_hotspot_model",
        }
    },
    {
        "domain": "plasma_physics",
        "era": "plasma_2021_approach",
        "year": 61,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "plasma_physics",
            "claim": "NIF 1.3 MJ yield shot: plasma implosion first exceeds Lawson ignition threshold. Hot-spot model validated.",
            "source": "Zylstra et al. (2022). Nature.",
            "status": "resolved",
            "era": "plasma_2021_approach",
        }
    },
]

# ── Domain C: Materials Science ───────────────────────────────────────────────
DOMAIN_C = [
    {
        "domain": "materials_science",
        "era": "mat_1970_glass_failure",
        "year": 10,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "materials_science",
            "claim": "Glass microsphere capsules shatter during laser compression. Surface roughness triggers mix.",
            "source": "Nuckolls et al. (1972). Nature.",
            "status": "failure",
            "era": "mat_1970_glass_failure",
        }
    },
    {
        "domain": "materials_science",
        "era": "mat_1990_beryllium_failure",
        "year": 30,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "materials_science",
            "claim": "Beryllium capsule ablation is non-uniform; beryllium hydride forms and poisons hot-spot. Fails.",
            "source": "Hammel et al. (1994). Physical Review Letters.",
            "status": "failure",
            "era": "mat_1990_beryllium_failure",
        }
    },
    {
        "domain": "materials_science",
        "era": "mat_2012_diamond_capsule",
        "year": 52,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "materials_science",
            "claim": "High-Density Carbon (diamond) capsule: survives compression, ablates cleanly, minimal mix. Surface roughness < 30nm achievable.",
            "source": "Döppner et al. (2012). Physical Review Letters.",
            "status": "resolved",
            "era": "mat_2012_diamond_capsule",
        }
    },
]

# ── Domain D: Target Geometry ─────────────────────────────────────────────────
DOMAIN_D = [
    {
        "domain": "target_geometry",
        "era": "geo_1972_direct_drive_failure",
        "year": 12,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "target_geometry",
            "claim": "Direct laser drive: beam imprint causes highly non-uniform ablation. Implosion asymmetry is fatal.",
            "source": "Brueckner & Jorna (1974). Reviews of Modern Physics.",
            "status": "failure",
            "era": "geo_1972_direct_drive_failure",
        }
    },
    {
        "domain": "target_geometry",
        "era": "geo_1975_hohlraum",
        "year": 15,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "target_geometry",
            "claim": "Indirect drive via gold hohlraum: laser heats cylinder walls, X-ray bath uniformly compresses capsule. Drive symmetry problem partially solved.",
            "source": "Nuckolls, J. (1972, declassified 1979). LLNL.",
            "status": "resolved",
            "era": "geo_1975_hohlraum",
        }
    },
    {
        "domain": "target_geometry",
        "era": "geo_2018_3d_symmetry",
        "year": 58,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "target_geometry",
            "claim": "3D radiation-hydrodynamics modeling enables laser cone-fraction tuning for <1% drive asymmetry. Precision geometry achieved.",
            "source": "Clark et al. (2019). Physical Review Letters.",
            "status": "resolved",
            "era": "geo_2018_3d_symmetry",
        }
    },
]

# ── Synthesis Node (all 4 domains converge) ───────────────────────────────────
SYNTHESIS = {
    "domain": "synthesis",
    "era": "nif_ignition_2022",
    "year": 62,
    "payload": {
        "domain": "synthesis",
        "claim": "NIF achieves fusion ignition (Dec 2022): 192 laser beams + diamond capsule + hohlraum geometry + hot-spot ignition = 3.15 MJ output from 2.05 MJ input. First man-made fusion ignition.",
        "source": "Abu-Shawareb et al. (2022). Physical Review Letters. DOI:10.1103/PhysRevLett.129.075001",
        "status": "validated_breakthrough",
        "era": "nif_ignition_2022",
        "domains_contributing": ["laser_physics", "plasma_physics", "materials_science", "target_geometry"],
    }
}

ALL_DOMAINS = [DOMAIN_A, DOMAIN_B, DOMAIN_C, DOMAIN_D]
ALL_DOMAIN_EVENTS = DOMAIN_A + DOMAIN_B + DOMAIN_C + DOMAIN_D


def _within_domain_failure_pairs(domain_events):
    """
    For each domain chain, return (failure_era, resolution_era) pairs
    so the corpus loader can mark the resolution as superseding the failure.
    """
    failure_pairs = {
        "laser_physics":    ("laser_2009_failure", "laser_2014_pulse_shaping"),
        "plasma_physics":   ("plasma_1980_rayleigh_taylor", "plasma_2015_hotspot_model"),
        "materials_science":("mat_1990_beryllium_failure", "mat_2012_diamond_capsule"),
        "target_geometry":  ("geo_1972_direct_drive_failure", "geo_1975_hohlraum"),
    }
    return failure_pairs


def load_corpus(kernel):
    """
    Ingest all four domain chains into Kosh, then create the synthesis node
    with an incoming edge from the final resolved event in each domain.

    Returns:
        node_ids: dict keyed by era string
        synthesis_id: int node id of the convergence node
    """
    now_ns = time.time_ns()
    node_ids = {}

    # ── Load each domain as an independent linear chain ───────────────────────
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

    # ── Mark within-domain failures as Contradicted by their resolutions ──────
    failure_pairs = _within_domain_failure_pairs(ALL_DOMAIN_EVENTS)
    for domain, (failure_era, resolution_era) in failure_pairs.items():
        if failure_era in node_ids and resolution_era in node_ids:
            kernel.insert_edge(
                source_id=node_ids[resolution_era],
                target_id=node_ids[failure_era],
                edge_type=99,
                edge_origin="Contradicted",
                edge_role="Mechanistic",
            )

    # ── Create the synthesis node with no linear parent ───────────────────────
    syn_ts = now_ns + SYNTHESIS["year"] * _YEAR_NS
    synthesis_id = kernel.insert_node(
        event_type=2,
        payload=SYNTHESIS["payload"],
        parent_id=None,
        documented_at_ns=syn_ts,
        valid_from_ns=syn_ts,
    )
    node_ids[SYNTHESIS["era"]] = synthesis_id

    # ── Connect the final resolved event from each domain to synthesis node ───
    domain_final_events = {
        "laser_physics":    "laser_2014_pulse_shaping",
        "plasma_physics":   "plasma_2021_approach",
        "materials_science":"mat_2012_diamond_capsule",
        "target_geometry":  "geo_2018_3d_symmetry",
    }
    for domain, final_era in domain_final_events.items():
        if final_era in node_ids:
            kernel.insert_edge(
                source_id=node_ids[final_era],
                target_id=synthesis_id,
                edge_type=2,
                edge_origin="Observed",
                edge_role="Causal",
            )

    return node_ids, synthesis_id
