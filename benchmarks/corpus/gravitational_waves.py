"""
benchmarks/corpus/gravitational_waves.py
==========================================
LIGO Gravitational Wave Detection Corpus — 5-Domain, 100-Year Consilience

Einstein predicted gravitational waves in 1916. Direct detection took 99 years.
Five independent research domains each failed individually before converging
on GW150914 (Sept 14, 2015) — the first direct detection of a gravitational wave
from a binary black hole merger.

Domain A — Theoretical Physics (General Relativity & GW existence debate)
Domain B — Experimental Physics (Weber bar detectors — famous failure)
Domain C — Laser Interferometry (Weiss/Drever/Thorne + LIGO prototype failures)
Domain D — Seismic & Noise Isolation (Earth vibration masked all signals for decades)
Domain E — Numerical Relativity & Signal Processing (waveform templates took 40 years)

Key structural difference from NIF fusion benchmark:
  - 100-year timeline vs 60-year (tests CDSS robustness across longer horizons)
  - One domain (B) is a famous COMPLETE RED HERRING — Weber's results were
    entirely fabricated/mistaken. CDSS must not penalise the synthesis for it.
  - Synthesis node has 5 independent inbound causal edges (vs 4 in fusion)
"""

import time

_YEAR_NS = 365 * 24 * 60 * 60 * 1_000_000_000
_BASE_NS = time.time_ns()


def _ts(year_offset):
    return _BASE_NS + year_offset * _YEAR_NS


# ── Domain A: Theoretical Physics ────────────────────────────────────────────
DOMAIN_A = [
    {
        "domain": "theoretical_physics",
        "era": "gr_1916_einstein_predicts",
        "year": 0,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "theoretical_physics",
            "claim": "Einstein (1916) derives gravitational waves as solutions to linearised field equations. Accelerating masses must radiate spacetime ripples.",
            "source": "Einstein, A. (1916). Approximative Integration of the Field Equations of Gravitation. Sitzungsberichte.",
            "status": "foundation",
            "era": "gr_1916_einstein_predicts",
        }
    },
    {
        "domain": "theoretical_physics",
        "era": "gr_1936_einstein_retracts",
        "year": 20,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "theoretical_physics",
            "claim": "Einstein & Rosen submit paper claiming gravitational waves are a mathematical artefact and do not physically exist. Paper is initially rejected by Physical Review.",
            "source": "Einstein & Rosen (1936). The Particle Problem in the General Theory. Phys. Rev. (retracted).",
            "status": "failure",
            "era": "gr_1936_einstein_retracts",
        }
    },
    {
        "domain": "theoretical_physics",
        "era": "gr_1957_pirani_resolves",
        "year": 41,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "theoretical_physics",
            "claim": "Pirani (1957) proves gravitational waves carry physical energy and exert tidal forces on test masses. They are real, detectable in principle. GR community consensus restored.",
            "source": "Pirani, F.A.E. (1957). On the Physical Significance of the Riemann Tensor. Acta Physica Polonica.",
            "status": "resolved",
            "era": "gr_1957_pirani_resolves",
        }
    },
]

# ── Domain B: Experimental Physics (Weber bars) ───────────────────────────────
DOMAIN_B = [
    {
        "domain": "experimental_physics",
        "era": "weber_1969_false_claim",
        "year": 53,
        "edge_origin": "Hypothetical",
        "edge_role": "Predictive",
        "payload": {
            "domain": "experimental_physics",
            "claim": "Joseph Weber claims detection of gravitational waves using aluminium bar resonant detectors. Reports multiple daily detections — far too many to be genuine.",
            "source": "Weber, J. (1969). Evidence for Discovery of Gravitational Radiation. Phys. Rev. Lett.",
            "status": "failure",
            "era": "weber_1969_false_claim",
        }
    },
    {
        "domain": "experimental_physics",
        "era": "weber_1974_refuted",
        "year": 58,
        "edge_origin": "Discovered",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "experimental_physics",
            "claim": "Seven independent labs fail to reproduce Weber's results. Statistical analysis reveals data manipulation. Bar detectors are 10^10 times too insensitive for any plausible GW source.",
            "source": "Garwin & Levine (1973); Tyson (1973); multiple PRL papers 1972-1975.",
            "status": "resolved",
            "era": "weber_1974_refuted",
        }
    },
    {
        "domain": "experimental_physics",
        "era": "hulse_taylor_1974_indirect",
        "year": 58,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "experimental_physics",
            "claim": "Hulse & Taylor discover binary pulsar PSR 1913+16. Its orbital decay precisely matches GR predictions for GW energy loss — first indirect evidence GW exist and carry energy. Nobel Prize 1993.",
            "source": "Hulse, R.A. & Taylor, J.H. (1975). ApJ Letters. Nobel Prize 1993.",
            "status": "resolved",
            "era": "hulse_taylor_1974_indirect",
        }
    },
]

# ── Domain C: Laser Interferometry ────────────────────────────────────────────
DOMAIN_C = [
    {
        "domain": "laser_interferometry",
        "era": "weiss_1972_proposal",
        "year": 56,
        "edge_origin": "Hypothetical",
        "edge_role": "Predictive",
        "payload": {
            "domain": "laser_interferometry",
            "claim": "Rainer Weiss (1972) proposes km-scale laser interferometer to detect GW via differential arm-length changes. Calculates all noise sources. Sensitivity needed: 10^-21 strain.",
            "source": "Weiss, R. (1972). Quarterly Progress Report, MIT RLE.",
            "status": "hypothesis",
            "era": "weiss_1972_proposal",
        }
    },
    {
        "domain": "laser_interferometry",
        "era": "proto_1983_too_noisy",
        "year": 67,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "laser_interferometry",
            "claim": "MIT 1.5m prototype and Caltech 40m prototype: laser shot noise, mirror thermal noise, and scattered light dominate. Orders of magnitude too noisy. Proof of concept only.",
            "source": "Drever et al. (1983). Caltech 40m Prototype Reports.",
            "status": "failure",
            "era": "proto_1983_too_noisy",
        }
    },
    {
        "domain": "laser_interferometry",
        "era": "ligo_2002_first_run",
        "year": 86,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "laser_interferometry",
            "claim": "Initial LIGO completes first science run (S1). Strain sensitivity ~10^-19 — still 100x too insensitive. No GW detected. Advanced LIGO redesign required.",
            "source": "Abbott et al. (2004). LIGO S1 Science Run Results. Phys. Rev. D.",
            "status": "failure",
            "era": "ligo_2002_first_run",
        }
    },
    {
        "domain": "laser_interferometry",
        "era": "advanced_ligo_2015",
        "year": 99,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "laser_interferometry",
            "claim": "Advanced LIGO achieves design sensitivity 10^-23 strain via Fabry-Perot cavities (280kW stored power), signal recycling, and 40kg fused silica mirrors. Detection threshold crossed.",
            "source": "Aasi et al. (2015). Advanced LIGO. Classical and Quantum Gravity.",
            "status": "resolved",
            "era": "advanced_ligo_2015",
        }
    },
]

# ── Domain D: Seismic & Noise Isolation ───────────────────────────────────────
DOMAIN_D = [
    {
        "domain": "seismic_isolation",
        "era": "seismic_1980s_wall",
        "year": 64,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "seismic_isolation",
            "claim": "Earth's seismic noise at 10Hz is 10^-9 m/sqrt(Hz). This is 10^10 times larger than the GW signal. Any detector built on solid ground is completely blind below 40Hz.",
            "source": "Peterson, J. (1993). USGS Open File Report. Noise models.",
            "status": "failure",
            "era": "seismic_1980s_wall",
        }
    },
    {
        "domain": "seismic_isolation",
        "era": "seismic_2002_quadruple",
        "year": 86,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "seismic_isolation",
            "claim": "Quadruple pendulum isolation system (HAM-ISI, BSC-ISI): 12-stage passive + active isolation reduces mirror motion to 10^-19 m at 10Hz. Seismic wall overcome.",
            "source": "Robertson et al. (2002); Matichard et al. (2015). Classical and Quantum Gravity.",
            "status": "resolved",
            "era": "seismic_2002_quadruple",
        }
    },
]

# ── Domain E: Numerical Relativity & Signal Processing ────────────────────────
DOMAIN_E = [
    {
        "domain": "numerical_relativity",
        "era": "numerical_1964_matched_filter",
        "year": 48,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "numerical_relativity",
            "claim": "Turin (1960) and Helstrom (1968): matched filter theory shows optimal detection of known waveforms in noise. Requires knowing the signal template in advance. GW waveform shapes unknown.",
            "source": "Turin, G.L. (1960). IRE Transactions. Helstrom, C. (1968). Statistical Theory of Signal Detection.",
            "status": "foundation",
            "era": "numerical_1964_matched_filter",
        }
    },
    {
        "domain": "numerical_relativity",
        "era": "numerical_1990s_unstable",
        "year": 74,
        "edge_origin": "Observed",
        "edge_role": "Mechanistic",
        "payload": {
            "domain": "numerical_relativity",
            "claim": "All numerical relativity codes for binary black hole (BBH) mergers crash within milliseconds due to coordinate singularity instabilities. Merger waveform shapes remain unknown.",
            "source": "Multiple NR groups, 1985-2004. Binary Black Hole Grand Challenge Alliance.",
            "status": "failure",
            "era": "numerical_1990s_unstable",
        }
    },
    {
        "domain": "numerical_relativity",
        "era": "numerical_2005_breakthrough",
        "year": 89,
        "edge_origin": "Discovered",
        "edge_role": "Causal",
        "payload": {
            "domain": "numerical_relativity",
            "claim": "Frans Pretorius (2005): first successful simulation of BBH merger through ringdown using generalised harmonic coordinates. Full waveform computed. Matched filter templates now buildable.",
            "source": "Pretorius, F. (2005). Evolution of Binary Black-Hole Spacetimes. Phys. Rev. Lett. 95, 121101.",
            "status": "resolved",
            "era": "numerical_2005_breakthrough",
        }
    },
]

# ── Synthesis Node ────────────────────────────────────────────────────────────
SYNTHESIS = {
    "domain": "synthesis",
    "era": "gw150914_detection_2015",
    "year": 99,
    "payload": {
        "domain": "synthesis",
        "claim": "GW150914 (Sept 14, 2015): LIGO detects gravitational waves from binary black hole merger 1.3 billion light-years away. Signal matches NR waveform template exactly. 5.1-sigma significance. Nobel Prize 2017.",
        "source": "Abbott et al. (LIGO Scientific Collaboration & Virgo Collaboration). (2016). Phys. Rev. Lett. 116, 061102.",
        "status": "validated_breakthrough",
        "era": "gw150914_detection_2015",
        "domains_contributing": [
            "theoretical_physics", "experimental_physics",
            "laser_interferometry", "seismic_isolation", "numerical_relativity"
        ],
    }
}

ALL_DOMAINS     = [DOMAIN_A, DOMAIN_B, DOMAIN_C, DOMAIN_D, DOMAIN_E]
ALL_DOMAIN_EVENTS = DOMAIN_A + DOMAIN_B + DOMAIN_C + DOMAIN_D + DOMAIN_E


def load_corpus(kernel):
    """
    Ingest all five domain chains and the synthesis node into Kosh.
    Returns (node_ids dict, synthesis_id int).
    """
    now_ns = time.time_ns()
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

    # ── Mark within-domain failures as Contradicted by their resolutions ──────
    failure_pairs = {
        "theoretical_physics": ("gr_1936_einstein_retracts",   "gr_1957_pirani_resolves"),
        "experimental_physics": ("weber_1969_false_claim",      "weber_1974_refuted"),
        "laser_interferometry": ("ligo_2002_first_run",         "advanced_ligo_2015"),
        "seismic_isolation":    ("seismic_1980s_wall",          "seismic_2002_quadruple"),
        "numerical_relativity": ("numerical_1990s_unstable",    "numerical_2005_breakthrough"),
    }
    for domain, (failure_era, resolution_era) in failure_pairs.items():
        if failure_era in node_ids and resolution_era in node_ids:
            kernel.insert_edge(
                source_id=node_ids[resolution_era],
                target_id=node_ids[failure_era],
                edge_type=99,
                edge_origin="Contradicted",
                edge_role="Mechanistic",
            )

    # ── Synthesis node (no linear parent) ────────────────────────────────────
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
        "theoretical_physics": "gr_1957_pirani_resolves",
        "experimental_physics": "hulse_taylor_1974_indirect",
        "laser_interferometry": "advanced_ligo_2015",
        "seismic_isolation":    "seismic_2002_quadruple",
        "numerical_relativity": "numerical_2005_breakthrough",
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
