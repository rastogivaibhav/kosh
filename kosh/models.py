import struct
from enum import Enum

from dataclasses import dataclass, field

class ReasoningMode(Enum):
    """Cognitive state of the Kosh reasoning engine."""
    EMPIRICAL   = "empirical"    # Waking State: strict facts only, aggressive pruning
    THEORETICAL = "theoretical"  # REM Sleep: free hypothetical exploration, no pruning
    BALANCED    = "balanced"     # Default: standard habituation and 24-hour pruning

@dataclass
class GovernancePolicy:
    prune_max_age_ns: int = 24 * 60 * 60 * 1_000_000_000  # 24 hours
    protect_high_resonance: float = 0.8  # Prevent pruning if resonance is above this
    habituation_rate: float = 0.5  # Decay rate for salience during reinforcement
    mode: ReasoningMode = field(default=ReasoningMode.BALANCED)

    @classmethod
    def from_mode(cls, mode: ReasoningMode) -> "GovernancePolicy":
        """Factory: builds a GovernancePolicy preset tuned for a given cognitive mode."""
        if mode == ReasoningMode.EMPIRICAL:
            # Waking State: demands evidence, composts hypotheses within 1 hour
            return cls(
                prune_max_age_ns=1 * 60 * 60 * 1_000_000_000,
                protect_high_resonance=0.95,
                habituation_rate=0.9,
                mode=mode
            )
        elif mode == ReasoningMode.THEORETICAL:
            # REM Sleep: maximum creative latitude, no pruning at all
            return cls(
                prune_max_age_ns=999 * 365 * 24 * 60 * 60 * 1_000_000_000,  # ~999 years
                protect_high_resonance=0.0,  # protect everything
                habituation_rate=0.1,         # very slow decay — let hypotheses grow freely
                mode=mode
            )
        else:
            # Balanced: sensible defaults
            return cls(mode=mode)

# Node: 72 bytes
# 0: id (uint64) - This represents the linear spatial index derived from (q, r)
# 8: ingested_at_ns (uint64) - 0 means the slot is empty
# 16: documented_at_ns (uint64)
# 24: valid_from_ns (uint64)
# 32: valid_until_ns (uint64)
# 40: event_type (uint64)
# 48: first_incoming_edge_idx (uint64)
# 56: payload_offset (uint64)
# 64: payload_size (uint64)
NODE_STRUCT = struct.Struct("<QQQQQQQQQ")
NODE_SIZE = NODE_STRUCT.size

# Edge: 48 bytes
# 0: source_node_id (uint64)
# 8: target_node_id (uint64)
# 16: edge_type (uint64)
# 24: provenance_flags (uint64) -> [4 bits Origin][4 bits Role][56 bits padding]
# 32: next_incoming_edge_idx (uint64)
# 40: salience (float32)
# 44: reinforcement_count (uint32)
EDGE_STRUCT = struct.Struct("<QQQQQfI")
EDGE_SIZE = EDGE_STRUCT.size

NULL_IDX = 0xFFFFFFFFFFFFFFFF

# Graphene Lattice Mapping Constants
GRID_RADIUS = 1000
GRID_DIAMETER = GRID_RADIUS * 2
MAX_LATTICE_NODES = GRID_DIAMETER * GRID_DIAMETER

def coord_to_idx(q: int, r: int) -> int:
    return (q + GRID_RADIUS) * GRID_DIAMETER + (r + GRID_RADIUS)

def idx_to_coord(idx: int) -> tuple[int, int]:
    r = (idx % GRID_DIAMETER) - GRID_RADIUS
    q = (idx // GRID_DIAMETER) - GRID_RADIUS
    return q, r

def get_hex_neighbors(q: int, r: int) -> list[tuple[int, int]]:
    return [
        (q + 1, r),
        (q + 1, r - 1),
        (q, r - 1),
        (q - 1, r),
        (q - 1, r + 1),
        (q, r + 1)
    ]

# Taxonomy Mapping
EDGE_ORIGIN_MAP = {
    "Observed":     0x0,
    "Discovered":   0x1,
    "Inferred":     0x2,
    "Reinforced":   0x3,
    "Hypothetical": 0x4,
    "Contradicted": 0x5,  # Explicitly refuted by later empirical evidence
}
EDGE_ORIGIN_REVERSE = {v: k for k, v in EDGE_ORIGIN_MAP.items()}

EDGE_ROLE_MAP = {
    "Mechanistic": 0x0,
    "Compressed": 0x1,
    "Analogical": 0x2,
    "Predictive": 0x3,
    "Causal": 0x4
}
EDGE_ROLE_REVERSE = {v: k for k, v in EDGE_ROLE_MAP.items()}

