"""
benchmarks/baseline.py
======================
A naive flat-retrieval baseline to compare against Kosh.

This simulates what a standard Vector DB or RAG retrieval system does:
it returns ALL documents equally, with no temporal awareness, no contradiction
detection, and no stability scoring. The caller must figure out which facts
are current vs. outdated.
"""


class NaiveBaseline:
    """
    In-memory flat document store. Models how a standard RAG/Vector DB behaves:
    every document is given equal retrieval weight regardless of its timestamp
    or whether it has been contradicted by a later fact.
    """

    def __init__(self):
        self._store: list[dict] = []

    def ingest(self, payload: dict):
        self._store.append(payload)

    def retrieve_all(self) -> list[dict]:
        """Return every document with equal weight — no filtering, no scoring."""
        return list(self._store)

    def retrieve_query(self, keyword: str) -> list[dict]:
        """Naive keyword match across all documents, oldest and newest alike."""
        keyword = keyword.lower()
        return [
            doc for doc in self._store
            if keyword in str(doc).lower()
        ]

    def summary(self) -> dict:
        return {
            "total_docs": len(self._store),
            "outdated_docs_surfaced": "unknown — baseline has no contradiction detection",
            "stability_score": "N/A — baseline has no stability model",
        }
