# app/kosh/linguistics/__init__.py
"""
kosh.linguistics
=================
Zero-dependency native linguistic engine for Kosh.

Inspired by the 2014 StoryScoring architecture (ScoreCalculators.cs,
RelevanceFinder.cs), modernised with continuous mathematics:
- Aho-Corasick Trie for O(N) multi-pattern token matching
- Continuous TF-IDF Unusualness scoring (replaces hard score steps)
- Sliding-window Coherence (replaces brittle ExtraWords thresholds)
- Ratio-based Abstraction classification
- Citation-anchored Causal Edge extraction

"""

from .lexicons import LEXICON
from .trie import AhoCorasickTrie
from .scorer import LinguisticScorer
from .extractor import DocumentExtractor

__all__ = ["LEXICON", "AhoCorasickTrie", "LinguisticScorer", "DocumentExtractor"]
