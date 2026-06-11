"""
app/kosh/adapters/native_ingestor.py
======================================
Item 8: External Evidence Adapters
Native ingestion of documents into the Kosh MemoryKernel.

Supports:
  - .md  (Markdown with optional YAML frontmatter)
  - .txt (plain text, treated as pure body)
  - Any file with extractable string content

Uses the kosh.linguistics DocumentExtractor to:
  1. Score raw text (Unusualness, Coherence, Abstraction)
  2. Auto-classify node status
  3. Wire causal edges via Aho-Corasick verb detection + citation anchoring
"""

import os
import glob

from kosh.linguistics import DocumentExtractor


class NativeIngestor:
    """
    Reads all documents from a directory and ingests them into Kosh,
    automatically scoring and wiring the provenance graph.
    """

    SUPPORTED_EXTENSIONS = (".md", ".txt")

    def __init__(self, kernel):
        self.kernel    = kernel
        self.extractor = DocumentExtractor(kernel)

    def ingest_directory(self, dir_path: str) -> dict:
        """
        Reads all supported files, sorts chronologically by year metadata,
        then performs a two-pass ingest:
          Pass 1 – Insert all nodes (collect id_map)
          Pass 2 – Wire all edges (requires complete id_map for resolution)
        Returns {doc_id: node_id} map.
        """
        files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            files.extend(glob.glob(os.path.join(dir_path, f"*{ext}")))

        if not files:
            return {}

        # Pre-parse all files to extract year for sorting
        raw_docs = []
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
            raw_docs.append((fpath, text))

        # Sort chronologically by year embedded in frontmatter or filename
        def _year_key(item):
            _, text = item
            import re
            m = re.search(r'^year:\s*(\d{4})', text, re.MULTILINE)
            if m:
                return int(m.group(1))
            # Fallback: try filename digits
            fname_m = re.search(r'(\d{4})', os.path.basename(item[0]))
            return int(fname_m.group(1)) if fname_m else 9999

        raw_docs.sort(key=_year_key)

        # Pass 1 – Insert all nodes, build id_map
        id_map: dict = {}
        doc_texts: list = []

        for fpath, text in raw_docs:
            # Extract doc_id from frontmatter or filename stem
            doc_id = self._extract_doc_id(fpath, text)
            year   = _year_key((fpath, text))

            node_id = self.extractor.ingest(
                text=text,
                doc_id=doc_id,
                domain=self._extract_domain(text),
                year=year,
                known_ids=None,   # No edge wiring on first pass
            )
            id_map[doc_id] = node_id
            doc_texts.append((doc_id, text, year))

        # Pass 2 – Re-wire edges now that all nodes exist
        for doc_id, text, year in doc_texts:
            node_id = id_map[doc_id]
            domain  = self._extract_domain(text)
            # Re-run extractor edge wiring only (node already exists, skip insert)
            body, fm_meta = self.extractor._strip_frontmatter(text)
            scoring = self.extractor.scorer.score(body)
            self.extractor._wire_edges(
                body        = body,
                doc_id      = doc_id,
                node_id     = node_id,
                ts          = 0,
                causal_hits = scoring["causal_hits"],
                fm_meta     = fm_meta,
                known_ids   = id_map,
            )

        return id_map

    def ingest_text(self, text: str, doc_id: str = "unknown",
                    domain: str = "unknown", year: int = 0,
                    known_ids: dict = None) -> int:
        """Ingest a single raw text string directly."""
        return self.extractor.ingest(
            text=text, doc_id=doc_id, domain=domain,
            year=year, known_ids=known_ids or {}
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_doc_id(self, fpath: str, text: str) -> str:
        import re
        m = re.search(r'^id:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if m:
            return m.group(1).strip()
        # Fallback: filename stem
        return os.path.splitext(os.path.basename(fpath))[0]

    def _extract_domain(self, text: str) -> str:
        import re
        m = re.search(r'^domain:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if m:
            return m.group(1).strip()
        return "unknown"
