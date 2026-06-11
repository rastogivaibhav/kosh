"""
app/kosh/linguistics/trie.py
==============================
Aho-Corasick Automaton — O(N) multi-pattern text matching.

This replaces the 2014 StoryScoring approach of iterating each word
in the lexicon and running a separate Regex.IsMatch() per word.
That was O(W * T) where W = lexicon size and T = text length.

The Aho-Corasick automaton preprocesses all patterns into a single
finite state machine. A single O(N) scan of the text finds ALL
matches simultaneously, where N = text length.

Zero external dependencies. Pure Python.
"""

from collections import deque
from typing import Dict, List, Tuple, Any


class AhoCorasickTrie:
    """
    Aho-Corasick multi-pattern search automaton.

    Build once from a pattern dictionary, then search any text in O(N).
    Each pattern maps to an arbitrary payload object (e.g. a dict of
    lexicon metadata).

    Usage:
        trie = AhoCorasickTrie()
        trie.add("refutes", {"edge_origin": "Contradicted"})
        trie.add("confirms", {"edge_origin": "Discovered"})
        trie.build()
        for pos, pattern, payload in trie.search(text):
            ...
    """

    def __init__(self):
        # goto[state][char] = next_state
        self._goto:   List[Dict[str, int]]  = [{}]
        # failure[state] = fallback_state
        self._fail:   List[int]             = [-1]
        # output[state] = list of (pattern, payload) matched here
        self._output: List[List[Tuple[str, Any]]] = [[]]
        self._built   = False
        self._n_states = 1  # state 0 = root

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def add(self, pattern: str, payload: Any = None):
        """Insert a single pattern into the trie (before build)."""
        if self._built:
            raise RuntimeError("Cannot add patterns after build().")
        node = 0
        for ch in pattern.lower():
            if ch not in self._goto[node]:
                self._goto[node][ch] = self._n_states
                self._goto.append({})
                self._fail.append(-1)
                self._output.append([])
                self._n_states += 1
            node = self._goto[node][ch]
        self._output[node].append((pattern, payload))

    def build(self):
        """Compute failure links via BFS (Aho-Corasick construction)."""
        queue = deque()
        root = 0
        # Root's children fail back to root
        for ch, s in self._goto[root].items():
            self._fail[s] = root
            queue.append(s)

        while queue:
            r = queue.popleft()
            for ch, s in self._goto[r].items():
                queue.append(s)
                # Follow failure links until we find a match or hit root
                state = self._fail[r]
                while state != root and ch not in self._goto[state]:
                    state = self._fail[state]
                self._fail[s] = self._goto[state].get(ch, root)
                if self._fail[s] == s:
                    self._fail[s] = root
                # Merge outputs along failure chain
                self._output[s] = (
                    self._output[s] + self._output[self._fail[s]]
                )
        self._built = True

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, text: str) -> List[Tuple[int, str, Any]]:
        """
        Scan text in O(N) and return all pattern hits.

        Returns list of (end_position, pattern, payload) tuples,
        sorted by position.

        Matches on word boundaries only (checks surrounding chars).
        """
        if not self._built:
            raise RuntimeError("Call build() before search().")
        results = []
        text_lower = text.lower()
        state = 0
        for i, ch in enumerate(text_lower):
            while state != 0 and ch not in self._goto[state]:
                state = self._fail[state]
            state = self._goto[state].get(ch, 0)
            for pattern, payload in self._output[state]:
                start = i - len(pattern) + 1
                # Word-boundary check
                before = text_lower[start - 1] if start > 0 else " "
                after  = text_lower[i + 1]     if i + 1 < len(text_lower) else " "
                if not (before.isalpha() or after.isalpha()):
                    results.append((i, pattern, payload))
        return results

    # ------------------------------------------------------------------
    # Convenience: build from a dict
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, pattern_dict: dict) -> "AhoCorasickTrie":
        """Build trie from {pattern: payload} mapping."""
        trie = cls()
        for pattern, payload in pattern_dict.items():
            trie.add(pattern, payload)
        trie.build()
        return trie

    @classmethod
    def from_set(cls, pattern_set, payload=None) -> "AhoCorasickTrie":
        """Build trie from a set/frozenset of patterns, all sharing payload."""
        trie = cls()
        for pattern in pattern_set:
            trie.add(pattern, payload)
        trie.build()
        return trie
