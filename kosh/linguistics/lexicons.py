"""
app/kosh/linguistics/lexicons.py
==================================
In-memory lexicon tables. Zero database dependencies.

Derived from the 2014 StoryScoring SQL tables (SS_RulesCPPLibrary,
SS_UnnecessaryWords, SS_Fillers, SS_CPPWordLibrary) but stored as
pure Python dictionaries and frozensets for O(1) lookup and Trie
construction.

The lexicons are divided into four functional layers:
  1. FILLER_WORDS      – High-frequency noise; penalised in Unusualness scoring.
  2. CAUSAL_VERBS      – Linguistic markers of causal/temporal relations.
  3. ABSTRACT_MARKERS  – Words indicating synthesis, deduction, or abstraction.
  4. CONCRETE_MARKERS  – Words indicating raw data, measurement, or observation.

Each causal verb entry carries:
  direction: 'refutes' | 'supports' | 'extends' | 'neutral'
  edge_origin: Kosh edge_origin string emitted when verb is found
  score: float weight applied to Coherence calculation
"""

# ---------------------------------------------------------------------------
# 1. FILLER WORDS – penalised in Unusualness (TF-IDF masking)
#    Derived from SS_UnnecessaryWords + SS_Fillers
# ---------------------------------------------------------------------------
FILLER_WORDS: frozenset = frozenset({
    # English structural fillers
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "as", "is", "was", "are",
    "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "shall",
    "can", "not", "no", "nor", "so", "yet", "both", "either", "neither",
    "each", "such", "this", "that", "these", "those", "its", "their",
    "our", "we", "he", "she", "it", "they", "i", "you", "us",
    # Academic filler (from StoryScoring methodology noise observed in papers)
    "however", "furthermore", "additionally", "therefore", "moreover",
    "subsequently", "accordingly", "consequently", "nevertheless",
    "although", "despite", "whereas", "whereby", "herein", "therein",
    "propose", "proposed", "present", "presented", "study", "paper",
    "work", "results", "approach", "method", "methods", "data",
    "analysis", "discussion", "conclusion", "introduction", "section",
    "table", "figure", "appendix", "et", "al", "ibid", "viz",
    # Spanish structural fillers (for multilingual support)
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
    "en", "que", "se", "con", "por", "para", "su", "sus", "al", "es",
    "son", "fue", "han", "como", "pero", "sin", "sobre", "entre",
})

# ---------------------------------------------------------------------------
# 2. CAUSAL VERBS – triggers for edge extraction (Coherence layer)
#    Derived from causal linguistics literature + StoryScoring rule detection
#    Each entry: (direction, edge_origin, coherence_weight)
# ---------------------------------------------------------------------------
CAUSAL_VERBS: dict = {
    # Contradiction / Refutation
    "refutes":       ("refutes",  "Contradicted", 0.95),
    "refuted":       ("refutes",  "Contradicted", 0.95),
    "contradicts":   ("refutes",  "Contradicted", 0.90),
    "contradicted":  ("refutes",  "Contradicted", 0.90),
    "disproves":     ("refutes",  "Contradicted", 0.90),
    "disproved":     ("refutes",  "Contradicted", 0.90),
    "disputes":      ("refutes",  "Contradicted", 0.80),
    "disputed":      ("refutes",  "Contradicted", 0.80),
    "challenges":    ("refutes",  "Contradicted", 0.75),
    "challenged":    ("refutes",  "Contradicted", 0.75),
    "rejects":       ("refutes",  "Contradicted", 0.70),
    "rejected":      ("refutes",  "Contradicted", 0.70),
    "incompatible":  ("refutes",  "Contradicted", 0.65),
    "inconsistent":  ("refutes",  "Contradicted", 0.60),
    "rechazamos":    ("refutes",  "Contradicted", 0.90),  # Spanish
    "refutamos":     ("refutes",  "Contradicted", 0.90),  # Spanish
    "contradice":    ("refutes",  "Contradicted", 0.85),  # Spanish
    # Resolution / Discovery
    "confirms":      ("supports", "Discovered",   0.90),
    "confirmed":     ("supports", "Discovered",   0.90),
    "resolves":      ("supports", "Discovered",   0.95),
    "resolved":      ("supports", "Discovered",   0.95),
    "validates":     ("supports", "Discovered",   0.85),
    "validated":     ("supports", "Discovered",   0.85),
    "corroborates":  ("supports", "Discovered",   0.80),
    "corroborated":  ("supports", "Discovered",   0.80),
    "proves":        ("supports", "Discovered",   0.90),
    "proved":        ("supports", "Discovered",   0.90),
    "demonstrates":  ("supports", "Discovered",   0.85),
    "demonstrated":  ("supports", "Discovered",   0.85),
    "confirma":      ("supports", "Discovered",   0.90),  # Spanish
    "demuestra":     ("supports", "Discovered",   0.85),  # Spanish
    # Extension / Building upon
    "extends":       ("extends",  "Observed",     0.75),
    "extended":      ("extends",  "Observed",     0.75),
    "builds":        ("extends",  "Observed",     0.70),
    "expands":       ("extends",  "Observed",     0.70),
    "improves":      ("extends",  "Observed",     0.65),
    "generalises":   ("extends",  "Observed",     0.65),
    "generalizes":   ("extends",  "Observed",     0.65),
    "unifies":       ("extends",  "Observed",     0.80),
    "synthesises":   ("extends",  "Observed",     0.85),
    "synthesizes":   ("extends",  "Observed",     0.85),
    "combines":      ("extends",  "Observed",     0.70),
    "integrates":    ("extends",  "Observed",     0.75),
}

# ---------------------------------------------------------------------------
# 3. ABSTRACT MARKERS – indicators of synthesis, deduction, high-level reasoning
#    Derived from StoryScoring abstractionScore >= 2 logic
# ---------------------------------------------------------------------------
ABSTRACT_MARKERS: frozenset = frozenset({
    # Scientific reasoning abstractions
    "theory", "theorem", "hypothesis", "conjecture", "principle",
    "framework", "model", "paradigm", "axiom", "corollary", "lemma",
    "inference", "deduction", "synthesis", "emergence", "convergence",
    "generalisation", "generalization", "abstraction", "implication",
    "mechanism", "causality", "causation", "correlation", "topology",
    # Mathematical abstractions
    "invariant", "symmetry", "manifold", "eigenvalue", "gradient",
    "divergence", "entropy", "probability", "distribution", "integral",
    "differential", "operator", "function", "space", "field", "group",
    # Cross-domain scientific markers
    "conservation", "equilibrium", "resonance", "coherence", "phase",
    "quantum", "relativistic", "thermodynamic", "stochastic",
    "deterministic", "chaotic", "nonlinear", "fractal", "attractor",
    # Biological abstractions
    "homeostasis", "metabolism", "morphogenesis", "phylogenesis",
    "transcription", "regulation", "signaling", "cascade",
    # Spanish abstract markers
    "teoría", "hipótesis", "principio", "síntesis", "mecanismo",
    "causalidad", "convergencia",
})

# ---------------------------------------------------------------------------
# 4. CONCRETE MARKERS – raw observation, measurement, empirical data
#    These keep the Abstraction score low (foundation nodes)
# ---------------------------------------------------------------------------
CONCRETE_MARKERS: frozenset = frozenset({
    # Empirical/measurement
    "measured", "measured", "observed", "detected", "found", "recorded",
    "sampled", "collected", "counted", "quantified", "calculated",
    "estimated", "reported", "identified", "isolated", "extracted",
    "sequenced", "mapped", "scanned", "imaged", "photographed",
    # Units and numbers indicators
    "km", "mg", "kg", "mm", "cm", "nm", "ppm", "ppb", "mev", "gev",
    "percent", "percentage", "ratio", "rate", "frequency", "magnitude",
    "amplitude", "concentration", "density", "pressure", "temperature",
    # Geological/physical observables
    "iridium", "anomaly", "layer", "stratum", "strata", "sediment",
    "crater", "ejecta", "impact", "boundary", "fossil", "specimen",
    # Spanish concrete markers
    "observamos", "medimos", "encontramos", "registramos", "detectamos",
    "cráter", "fósil", "estrato", "medición",
})

# ---------------------------------------------------------------------------
# Combined export
# ---------------------------------------------------------------------------
LEXICON = {
    "fillers":   FILLER_WORDS,
    "causal":    CAUSAL_VERBS,
    "abstract":  ABSTRACT_MARKERS,
    "concrete":  CONCRETE_MARKERS,
}
