"""
app/kosh/linguistics/scorer.py
================================
Three-dimensional linguistic scorer — the modernised port of the 2014
StoryScoring engine (ScoreCalculators.cs).

The 2014 system used discrete 0/1/2/3 integer steps.
This implementation uses continuous mathematics [0.0, 1.0]:

  Dimension 1: Unusualness  → TF-IDF weighted fractal-window score
                              (replaces UnusualnessScoreCalculator)
  Dimension 2: Coherence    → Sliding-window causal-verb density
                              (replaces CoherenceScoreCalculator)
  Dimension 3: Abstraction  → Abstract/Concrete token ratio with
                              filler-penalised denominator
                              (replaces AbstractionScoreCalculator)

All three dimensions feed into:
  - `node_status`  : automatic classification ('foundation', 'failure',
                     'resolved', 'synthesis', 'validated_breakthrough')
  - `resonance`    : the composite signal strength for graph retrieval

Zero external dependencies. All computation is done with stdlib math.
"""

import math
import re
from typing import List, Dict, Any, Tuple

from .lexicons import FILLER_WORDS, ABSTRACT_MARKERS, CONCRETE_MARKERS, CAUSAL_VERBS
from .trie import AhoCorasickTrie


# ---------------------------------------------------------------------------
# Build tries once at import time (Aho-Corasick construction is O(P))
# ---------------------------------------------------------------------------
_FILLER_TRIE   = AhoCorasickTrie.from_set(FILLER_WORDS)
_ABSTRACT_TRIE = AhoCorasickTrie.from_set(ABSTRACT_MARKERS)
_CONCRETE_TRIE = AhoCorasickTrie.from_set(CONCRETE_MARKERS)
_CAUSAL_TRIE   = AhoCorasickTrie.from_dict(
    {k: v for k, v in CAUSAL_VERBS.items()}
)

# Window size for fractal sliding-window (in tokens)
WINDOW_SIZE = 64
WINDOW_STEP = 32


class LinguisticScorer:
    """
    Evaluates a raw text document across three orthogonal dimensions.

    Call `score(text)` to receive a `ScoringResult` dict.
    """

    def score(self, text: str) -> Dict[str, Any]:
        """
        Returns a dict with:
          unusualness  float [0,1]  – signal density / noise resistance
          coherence    float [0,1]  – causal structure density
          abstraction  float [0,1]  – ratio of abstract to concrete content
          status       str          – auto-classified node status
          resonance    float [0,1]  – composite signal strength
          causal_hits  list         – raw causal verb hits for edge extraction
          windows      list         – per-window unusualness scores (for debug)
        """
        tokens = self._tokenise(text)
        if not tokens:
            return self._null_result()

        tf_idf_weights   = self._compute_tfidf(tokens)
        windows          = self._fractal_windows(tokens, tf_idf_weights)
        unusualness      = self._unusualness(windows)
        coherence, hits  = self._coherence(text, tokens)
        abstraction      = self._abstraction(tokens, tf_idf_weights)
        status           = self._classify(unusualness, coherence, abstraction)
        resonance        = self._composite_resonance(
                               unusualness, coherence, abstraction)

        return {
            "unusualness":  unusualness,
            "coherence":    coherence,
            "abstraction":  abstraction,
            "status":       status,
            "resonance":    resonance,
            "causal_hits":  hits,
            "windows":      windows,
            "token_count":  len(tokens),
        }

    # ------------------------------------------------------------------
    # 1. Unusualness — TF-IDF Fractal Window
    # ------------------------------------------------------------------

    def _compute_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Compute a TF-IDF-like weight for every token in the document.
        TF  = relative frequency of the token.
        IDF = log(1 / (tf + eps)) normalised by max_idf.
        Filler tokens receive weight 0.
        """
        n = len(tokens)
        freq: Dict[str, int] = {}
        for t in tokens:
            if t not in FILLER_WORDS:
                freq[t] = freq.get(t, 0) + 1

        if not freq:
            return {t: 0.0 for t in tokens}

        max_freq = max(freq.values())
        weights: Dict[str, float] = {}
        for t in tokens:
            if t in FILLER_WORDS:
                weights[t] = 0.0
            else:
                tf  = freq.get(t, 0) / max_freq
                # Rare words get high IDF; common ones get low IDF
                idf = math.log(n / (freq.get(t, 1)))
                weights[t] = tf * idf

        # Normalise to [0, 1]
        max_w = max(weights.values()) if weights else 1.0
        if max_w > 0:
            weights = {k: v / max_w for k, v in weights.items()}
        return weights

    def _fractal_windows(self, tokens: List[str],
                         weights: Dict[str, float]) -> List[float]:
        """
        Slide a window over the token sequence. In each window, compute
        the mean TF-IDF weight of non-filler tokens.
        Returns list of window scores. The peak is the Unusualness signal.
        """
        if len(tokens) <= WINDOW_SIZE:
            signal = [weights.get(t, 0.0) for t in tokens]
            return [sum(signal) / len(signal)] if signal else [0.0]

        scores = []
        for start in range(0, len(tokens) - WINDOW_SIZE + 1, WINDOW_STEP):
            window = tokens[start: start + WINDOW_SIZE]
            non_filler = [weights.get(t, 0.0)
                          for t in window if t not in FILLER_WORDS]
            score = (sum(non_filler) / len(non_filler)) if non_filler else 0.0
            scores.append(score)
        return scores

    def _unusualness(self, windows: List[float]) -> float:
        """
        Peak local resonance across all windows.
        The 2014 system took a hard max(score); we smooth it with a
        sigmoid to produce a continuous value [0, 1].
        """
        if not windows:
            return 0.0
        peak = max(windows)
        # Sigmoid centred at 0.5 with gain 8
        return 1.0 / (1.0 + math.exp(-8.0 * (peak - 0.5)))

    # ------------------------------------------------------------------
    # 2. Coherence — Sliding-window causal verb density
    # ------------------------------------------------------------------

    def _coherence(self, text: str, tokens: List[str]) \
            -> Tuple[float, List[Dict]]:
        """
        Scan the full text with the Aho-Corasick causal verb trie.
        Each hit contributes its verb weight to the Coherence score.
        Returns (coherence_score, list_of_hit_dicts).
        """
        hits_raw = _CAUSAL_TRIE.search(text)
        hits = []
        total_weight = 0.0

        for pos, pattern, payload in hits_raw:
            direction, edge_origin, weight = payload
            hits.append({
                "position":    pos,
                "verb":        pattern,
                "direction":   direction,
                "edge_origin": edge_origin,
                "weight":      weight,
            })
            total_weight += weight

        n_tokens = max(len(tokens), 1)
        # Raw density: sum of causal weights per 100 tokens
        density = (total_weight / n_tokens) * 100.0
        # Sigmoid: saturates at ~3 causal verbs per 100 tokens
        coherence = 1.0 / (1.0 + math.exp(-1.5 * (density - 2.0)))
        return round(coherence, 4), hits

    # ------------------------------------------------------------------
    # 3. Abstraction — Abstract/Concrete token ratio
    # ------------------------------------------------------------------

    def _abstraction(self, tokens: List[str],
                     weights: Dict[str, float]) -> float:
        """
        Modernised AbstractionScoreCalculator.
        Ratio of weighted abstract tokens to (abstract + concrete).
        Filler tokens are excluded from both numerator and denominator.
        """
        abstract_w  = 0.0
        concrete_w  = 0.0

        abstract_hits = _ABSTRACT_TRIE.search(" ".join(tokens))
        concrete_hits = _CONCRETE_TRIE.search(" ".join(tokens))

        for _, pattern, _ in abstract_hits:
            abstract_w += weights.get(pattern, 0.1)

        for _, pattern, _ in concrete_hits:
            concrete_w += weights.get(pattern, 0.1)

        denom = abstract_w + concrete_w
        if denom < 1e-9:
            return 0.5  # neutral – cannot determine
        return round(abstract_w / denom, 4)

    # ------------------------------------------------------------------
    # 4. Status Classification — Continuous thresholds
    # ------------------------------------------------------------------

    def _classify(self, unusualness: float, coherence: float,
                  abstraction: float) -> str:
        """
        Automatic node status classification. Modernised from the 2014
        hard switch-case logic to continuous threshold ranges.

        Thresholds inspired by the 2014 scorer's 0/1/2/3 grades,
        remapped to continuous [0, 1]:
          0 → 0.0–0.3  (failure / noise)
          1 → 0.3–0.5  (foundation / observation)
          2 → 0.5–0.7  (resolved / validated)
          3 → 0.7–1.0  (breakthrough / synthesis)
        """
        # Pure noise / incoherent text
        if unusualness < 0.30 and coherence < 0.30:
            return "failure"

        # Raw empirical, concrete, well-measured – foundation science
        if abstraction < 0.35 and unusualness >= 0.30:
            return "foundation"

        # Text that contradicts but doesn't fully resolve
        if coherence >= 0.45 and abstraction < 0.55:
            return "resolved"

        # Highly abstract, highly coherent, high unusualness = synthesis
        if abstraction >= 0.65 and coherence >= 0.60 and unusualness >= 0.60:
            return "validated_breakthrough"

        # Abstract synthesis without full unusualness yet
        if abstraction >= 0.55 and coherence >= 0.50:
            return "synthesis"

        # Default: the text is an intermediate observation
        return "foundation"

    # ------------------------------------------------------------------
    # 5. Composite Resonance
    # ------------------------------------------------------------------

    def _composite_resonance(self, unusualness: float, coherence: float,
                              abstraction: float) -> float:
        """
        Single composite score for graph ranking.
        Weights match the intuition of the 2014 system:
          Unusualness  0.45 – dominant signal (rare content wins)
          Coherence    0.35 – structural causal binding
          Abstraction  0.20 – synthesis bonus
        """
        return round(
            0.45 * unusualness + 0.35 * coherence + 0.20 * abstraction, 4
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tokenise(self, text: str) -> List[str]:
        """Lowercase, strip punctuation, split on whitespace."""
        clean = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text)
        return [t.lower() for t in clean.split() if t.strip()]

    def _null_result(self) -> Dict[str, Any]:
        return {
            "unusualness":  0.0,
            "coherence":    0.0,
            "abstraction":  0.5,
            "status":       "failure",
            "resonance":    0.0,
            "causal_hits":  [],
            "windows":      [],
            "token_count":  0,
        }
