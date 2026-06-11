"""
app/kosh/linguistics/extractor.py
====================================
DocumentExtractor — ties together the LinguisticScorer and the
Kosh MemoryKernel to perform full native document ingestion.

This replaces the 2014 ProcessStories.ProcessSFile() pipeline but
instead of writing to SQL, it writes directly into the Kosh mmap graph.

Pipeline:
  1. Parse raw text (any format: .md frontmatter stripped, raw .txt,
     plain strings from API feeds, PDF text dumps, etc.)
  2. Run LinguisticScorer → get Unusualness, Coherence, Abstraction
  3. Auto-classify node status
  4. Insert node into Kosh kernel
  5. Scan causal_hits → resolve citation anchors → insert edges

Citation anchor patterns supported:
  - [1], [2], [10]          (numeric inline refs)
  - (Alvarez, 1980)         (author-year)
  - (Author et al., 2023)   (author et al.)
  - alvarez_1980            (slug IDs from frontmatter)

Zero external dependencies. Pure Python + stdlib re.
"""

import re
from typing import Dict, List, Optional, Any

from .scorer import LinguisticScorer

# Synthetic epoch base (1970)
_YEAR_NS  = 365 * 24 * 60 * 60 * 1_000_000_000

# Regex patterns for citation anchor extraction
_CITATION_PATTERNS = [
    # Numeric: [1], [12], [1,2,3]
    re.compile(r"\[(\d+(?:,\s*\d+)*)\]"),
    # Author-year: (Alvarez, 1980) or (Alvarez et al., 1980)
    re.compile(r"\(([A-Z][a-zA-ZÀ-ÿ\-]+(?:\s+et\s+al\.?)?,?\s*\d{4})\)"),
    # Slug references embedded in text: "alvarez_1980" or "ref:alvarez_1980"
    re.compile(r"\b([a-z][a-z0-9_]{3,})\b"),
]

# Markdown frontmatter block pattern
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_FM_FIELD_RE    = re.compile(r'^(\w+):\s*"?([^"\n]+)"?', re.MULTILINE)


class DocumentExtractor:
    """
    Ingests a raw document (string) into the Kosh MemoryKernel.

    Usage:
        extractor = DocumentExtractor(kernel)
        node_id = extractor.ingest(text, doc_id="alvarez_1980",
                                   domain="geology", year=1980,
                                   known_ids={"alvarez_1980": node_id_ref})
    """

    def __init__(self, kernel):
        self.kernel  = kernel
        self.scorer  = LinguisticScorer()

    def ingest(
        self,
        text:      str,
        doc_id:    str          = "unknown",
        domain:    str          = "unknown",
        year:      int          = 0,
        known_ids: Dict[str, int] = None,   # slug → Kosh node_id map
    ) -> int:
        """
        Full pipeline: parse → score → classify → insert node → wire edges.
        Returns the Kosh node_id of the inserted document.
        """
        # 1. Strip markdown frontmatter if present; merge metadata
        body, fm_meta = self._strip_frontmatter(text)
        if fm_meta.get("id"):
            doc_id = fm_meta["id"]
        if fm_meta.get("domain"):
            domain = fm_meta["domain"]
        if fm_meta.get("year"):
            try:
                year = int(fm_meta["year"])
            except ValueError:
                pass

        # 2. Score the body text
        result = self.scorer.score(body)

        # 3. Build timestamp (relative to 1970)
        ts = int(max(year - 1970, 0) * _YEAR_NS)

        # 4. Insert the node
        payload = {
            "domain":       domain,
            "claim":        body[:2048],   # store first 2 KB of raw claim
            "source":       doc_id,
            "status":       fm_meta.get("status", result["status"]),
            "era":          doc_id,
            "unusualness":  result["unusualness"],
            "coherence":    result["coherence"],
            "abstraction":  result["abstraction"],
            "resonance":    result["resonance"],
        }

        node_id = self.kernel.insert_node(
            event_type=1,
            payload=payload,
            parent_id=None,
            documented_at_ns=ts,
            valid_from_ns=ts,
        )

        # 5. Wire causal edges if we have a known_ids map
        if known_ids:
            self._wire_edges(
                body, doc_id, node_id, ts, result["causal_hits"],
                fm_meta, known_ids
            )

        return node_id

    # ------------------------------------------------------------------
    # Edge Wiring
    # ------------------------------------------------------------------

    def _wire_edges(
        self,
        body:       str,
        doc_id:     str,
        node_id:    int,
        ts:         int,
        causal_hits: List[Dict],
        fm_meta:    Dict,
        known_ids:  Dict[str, int],
    ):
        """
        For each causal verb hit, scan a context window around it and
        try to resolve a citation anchor to a known node_id.
        If found, insert the appropriate Kosh edge.
        """
        body_lower = body.lower()

        # Frontmatter explicit targets override auto-extraction
        explicit_targets = fm_meta.get("targets", [])
        if isinstance(explicit_targets, str):
            explicit_targets = [t.strip() for t in
                                explicit_targets.strip("[]").split(",")
                                if t.strip()]

        if explicit_targets:
            origin = fm_meta.get("origin", "Observed")
            for target_slug in explicit_targets:
                target_id = known_ids.get(target_slug)
                if target_id:
                    if "Contradicted" in origin:
                        self.kernel.insert_edge(
                            source_id=node_id,
                            target_id=target_id,
                            edge_type=99,
                            edge_origin="Contradicted",
                            edge_role=fm_meta.get("role", "Causal"),
                        )
                    else:
                        self.kernel.insert_edge(
                            source_id=target_id,
                            target_id=node_id,
                            edge_type=2,
                            edge_origin=origin,
                            edge_role=fm_meta.get("role", "Causal"),
                        )
            return

        # Auto-extract from causal verb hits
        for hit in causal_hits:
            pos        = hit["position"]
            edge_origin = hit["edge_origin"]
            direction  = hit["direction"]

            # Extract 200-char context window around the verb
            ctx_start = max(0, pos - 100)
            ctx_end   = min(len(body), pos + 100)
            context   = body[ctx_start:ctx_end]

            resolved_ids = self._resolve_citations(context, known_ids, doc_id)

            for target_slug, target_id in resolved_ids.items():
                if edge_origin == "Contradicted":
                    self.kernel.insert_edge(
                        source_id=node_id,
                        target_id=target_id,
                        edge_type=99,
                        edge_origin="Contradicted",
                        edge_role="Causal",
                    )
                else:
                    self.kernel.insert_edge(
                        source_id=target_id,
                        target_id=node_id,
                        edge_type=2,
                        edge_origin=edge_origin,
                        edge_role="Causal",
                    )

    def _resolve_citations(
        self,
        context:   str,
        known_ids: Dict[str, int],
        self_id:   str,
    ) -> Dict[str, int]:
        resolved = {}
        for pat in _CITATION_PATTERNS:
            for m in pat.finditer(context):
                raw = m.group(1)
                slug = self._normalise_slug(raw, known_ids)
                if slug and slug != self_id and slug in known_ids:
                    resolved[slug] = known_ids[slug]
        return resolved

    def _normalise_slug(self, raw: str, known_ids: Dict[str, int]) -> str:
        """Convert a citation string to a slug: 'Alvarez, 1980' → 'alvarez_1980'."""
        # Fallback: return raw as-is if it's already a valid slug
        cleaned = re.sub(r"[^a-z0-9_]", "_", raw.lower()).strip("_")
        if cleaned in known_ids:
            return cleaned
        
        # Remove 'et al.' noise
        raw_stripped = re.sub(r"\s*et\s+al\.?", "", raw, flags=re.IGNORECASE)
        # Extract year if present
        year_m = re.search(r"(?:\b|_|-)(\d{4})(?:\b|_|-)", raw_stripped)
        year   = year_m.group(1) if year_m else ""
        # Extract first word as author token
        author = re.sub(r"[^a-zA-ZÀ-ÿ]", "", raw_stripped.split(",")[0]).lower()
        if author and year:
            return f"{author}_{year}"
        if author:
            return author
        return cleaned

    # ------------------------------------------------------------------
    # Markdown Frontmatter Parser
    # ------------------------------------------------------------------

    def _strip_frontmatter(self, text: str) -> tuple:
        """
        If text starts with YAML frontmatter (--- ... ---), strip it
        and return (body, meta_dict).
        Otherwise return (text, {}).
        """
        m = _FRONTMATTER_RE.match(text)
        if not m:
            return text, {}

        fm_block = m.group(1)
        body     = text[m.end():]
        meta     = {}

        for field_m in _FM_FIELD_RE.finditer(fm_block):
            key = field_m.group(1).strip()
            val = field_m.group(2).strip().strip('"').strip("'")
            meta[key] = val

        # targets is a special list field
        targets_m = re.search(r'^targets:\s*\[([^\]]*)\]',
                               fm_block, re.MULTILINE)
        if targets_m:
            raw_targets = targets_m.group(1)
            meta["targets"] = [
                t.strip().strip('"').strip("'")
                for t in raw_targets.split(",")
                if t.strip()
            ]

        return body.strip(), meta
