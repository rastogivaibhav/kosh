import mmap
import os
import struct
import time
import msgpack
from collections import deque
import math
from .models import (
    NODE_STRUCT, NODE_SIZE, EDGE_STRUCT, EDGE_SIZE, NULL_IDX,
    EDGE_ORIGIN_MAP, EDGE_ROLE_MAP, EDGE_ORIGIN_REVERSE, EDGE_ROLE_REVERSE,
    MAX_LATTICE_NODES, coord_to_idx, idx_to_coord, get_hex_neighbors,
    GovernancePolicy
)

HEADER_STRUCT = struct.Struct("<QQQ") # node_count, edge_count, heap_ptr
HEADER_SIZE = 4096
MAX_EDGES = 8_000_000

# --- Security Caps ---
# PATCH-1 (Heap Overflow): Max bytes any single payload may occupy in the heap.
MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB hard cap per node
# PATCH-2 (OOM Attack): Any p_size read from the file that exceeds this is treated as corruption.
MAX_READ_PAYLOAD_BYTES = 10 * 1024 * 1024
# PATCH-3 (Lattice BFS DoS): Maximum BFS hops before giving up and jumping to a free outer sector.
MAX_BFS_STEPS = 4096

NODE_BLOCK_OFFSET = HEADER_SIZE
EDGE_BLOCK_OFFSET = NODE_BLOCK_OFFSET + (MAX_LATTICE_NODES * NODE_SIZE)
HEAP_BLOCK_OFFSET = EDGE_BLOCK_OFFSET + (MAX_EDGES * EDGE_SIZE)

class MemoryKernel:
    def __init__(self, filepath, max_file_size=1024 * 1024 * 1024):
        self.filepath = filepath
        self.max_file_size = max_file_size
        
        is_new = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
        if is_new:
            with open(filepath, "wb") as f:
                f.seek(max_file_size - 1)
                f.write(b'\0')
                
        self.file = open(filepath, "r+b")
        self.mm = mmap.mmap(self.file.fileno(), max_file_size, access=mmap.ACCESS_WRITE)
        
        if is_new:
            self._write_header(0, 0, HEAP_BLOCK_OFFSET)
        
        self.node_count, self.edge_count, self.heap_ptr = self._read_header()

    def _read_header(self):
        return HEADER_STRUCT.unpack_from(self.mm, 0)

    def _write_header(self, node_count, edge_count, heap_ptr):
        HEADER_STRUCT.pack_into(self.mm, 0, node_count, edge_count, heap_ptr)

    def _get_node_offset(self, node_id):
        return NODE_BLOCK_OFFSET + (node_id * NODE_SIZE)

    def _get_edge_offset(self, edge_idx):
        return EDGE_BLOCK_OFFSET + (edge_idx * EDGE_SIZE)

    def _is_slot_empty(self, idx: int) -> bool:
        if idx < 0 or idx >= MAX_LATTICE_NODES:
            return False
        node_offset = self._get_node_offset(idx)
        ingested_at = struct.unpack_from("<Q", self.mm, node_offset + 8)[0]
        return ingested_at == 0

    def _allocate_node_idx(self, parent_id: int = None) -> int:
        start_q, start_r = (0, 0)
        if parent_id is not None:
            start_q, start_r = idx_to_coord(parent_id)
            
        queue = deque([(start_q, start_r)])
        visited = set([(start_q, start_r)])
        steps = 0
        
        while queue:
            q, r = queue.popleft()
            steps += 1

            # PATCH-3 (Lattice Saturation Sinkhole DoS):
            # If we have scanned too many filled neighbours without finding a slot,
            # jump radially outward to avoid an O(N) freeze on dense clusters.
            if steps > MAX_BFS_STEPS:
                import random
                jump_q = start_q + random.randint(GRID_RADIUS // 2, GRID_RADIUS - 1)
                jump_r = start_r + random.randint(GRID_RADIUS // 2, GRID_RADIUS - 1)
                queue = deque([(jump_q, jump_r)])
                visited.add((jump_q, jump_r))
                steps = 0

            idx = coord_to_idx(q, r)
            
            if 0 <= idx < MAX_LATTICE_NODES:
                if self._is_slot_empty(idx):
                    return idx
                    
            for nq, nr in get_hex_neighbors(q, r):
                if (nq, nr) not in visited:
                    visited.add((nq, nr))
                    queue.append((nq, nr))
                    
        raise Exception("Graphene Lattice is fully saturated!")

    def insert_node(self, event_type: int, payload: dict, parent_id: int = None,
                    edge_origin: str = "Observed", edge_role: str = "Causal",
                    documented_at_ns: int = None, valid_from_ns: int = None, valid_until_ns: int = None) -> int:
        
        node_id = self._allocate_node_idx(parent_id)
        
        payload_bytes = msgpack.packb(payload)
        payload_size = len(payload_bytes)

        # PATCH-1 (Heap Overflow / Payload Size Guard):
        if payload_size > MAX_PAYLOAD_BYTES:
            raise ValueError(
                f"Payload too large: {payload_size} bytes exceeds MAX_PAYLOAD_BYTES ({MAX_PAYLOAD_BYTES}). "
                "Compress or chunk the payload before inserting."
            )

        payload_offset = self.heap_ptr
        remaining = self.max_file_size - self.heap_ptr
        if payload_size > remaining:
            raise IOError(
                f"Kosh heap is full: {remaining} bytes left, need {payload_size}. "
                "Vacuum and compact the database."
            )

        self.mm[payload_offset:payload_offset + payload_size] = payload_bytes
        self.heap_ptr += payload_size
        
        # Timestamps
        ingested_at_ns = time.time_ns()
        doc_at = documented_at_ns if documented_at_ns else ingested_at_ns
        v_from = valid_from_ns if valid_from_ns else doc_at
        v_until = valid_until_ns if valid_until_ns else NULL_IDX
        
        node_offset = self._get_node_offset(node_id)
        
        # NODE_STRUCT: id, ingested, doc, v_from, v_until, type, first_edge, p_offset, p_size
        NODE_STRUCT.pack_into(
            self.mm, node_offset,
            node_id, ingested_at_ns, doc_at, v_from, v_until,
            event_type, NULL_IDX, payload_offset, payload_size
        )
        
        self.node_count += 1
        self._write_header(self.node_count, self.edge_count, self.heap_ptr)
        
        if parent_id is not None:
            self.insert_edge(source_id=parent_id, target_id=node_id, edge_type=1,
                             edge_origin=edge_origin, edge_role=edge_role)
            
        return node_id

    def insert_edge(self, source_id: int, target_id: int, edge_type: int,
                    edge_origin: str = "Observed", edge_role: str = "Causal"):
        edge_idx = self.edge_count
        
        target_node_offset = self._get_node_offset(target_id)
        target_node_data = list(NODE_STRUCT.unpack_from(self.mm, target_node_offset))
        current_first_incoming = target_node_data[6] # 6th index is first_incoming_edge_idx
        
        # Bit-pack provenance
        o_int = EDGE_ORIGIN_MAP.get(edge_origin, 0)
        r_int = EDGE_ROLE_MAP.get(edge_role, 4) # default causal
        provenance_flags = (o_int << 4) | r_int
        
        # EDGE_STRUCT: source, target, type, provenance, next_edge, salience, reinforcement_count
        edge_offset = self._get_edge_offset(edge_idx)
        EDGE_STRUCT.pack_into(self.mm, edge_offset, 
                              source_id, target_id, edge_type, provenance_flags, current_first_incoming,
                              1.0, 0)
        
        target_node_data[6] = edge_idx
        NODE_STRUCT.pack_into(self.mm, target_node_offset, *target_node_data)
        
        self.edge_count += 1
        self._write_header(self.node_count, self.edge_count, self.heap_ptr)

    def get_node_payload(self, node_id: int) -> dict:
        node_offset = self._get_node_offset(node_id)
        data = NODE_STRUCT.unpack_from(self.mm, node_offset)
        p_offset = data[7]
        p_size = data[8]
        if p_size == 0:
            return {}

        # PATCH-2 (Exabyte OOM Attack): Clamp p_size against a safe maximum before
        # slicing the mmap buffer. A tampered file could store 0xFFFFFFFFFFFFFFFF here.
        if p_size > MAX_READ_PAYLOAD_BYTES:
            raise ValueError(
                f"Corrupt node {node_id}: p_size={p_size} exceeds safety cap. "
                "File may have been tampered with."
            )

        payload_bytes = self.mm[p_offset:p_offset + p_size]

        # PATCH-4 (MsgPack Recursion Bomb): Enforce a strict recursion depth cap.
        return msgpack.unpackb(payload_bytes, max_bin_len=MAX_READ_PAYLOAD_BYTES, max_array_len=65536, max_map_len=65536)

    def get_incoming_edges(self, target_id: int):
        edges = []
        node_offset = self._get_node_offset(target_id)
        edge_idx = NODE_STRUCT.unpack_from(self.mm, node_offset)[6]
        
        while edge_idx != NULL_IDX:
            edge_offset = self._get_edge_offset(edge_idx)
            source_id, targ_id, e_type, prov_flags, next_idx, salience, reinf_count = EDGE_STRUCT.unpack_from(self.mm, edge_offset)
            
            o_int = (prov_flags >> 4) & 0xF
            r_int = prov_flags & 0xF
            
            origin_str = EDGE_ORIGIN_REVERSE.get(o_int, "Unknown")
            role_str = EDGE_ROLE_REVERSE.get(r_int, "Unknown")
            
            edges.append({
                "edge_idx": edge_idx,
                "source": source_id, 
                "type": e_type,
                "provenance": f"Origin: {origin_str}, Role: {role_str}",
                "origin": origin_str,
                "role": role_str,
                "salience": salience,
                "reinforcement_count": reinf_count
            })
            edge_idx = next_idx
            
        return edges

    def reinforce_edge(self, edge_idx: int, policy: GovernancePolicy = None):
        if policy is None:
            policy = GovernancePolicy()
            
        edge_offset = self._get_edge_offset(edge_idx)
        data = list(EDGE_STRUCT.unpack_from(self.mm, edge_offset))
        
        # data[5] is salience, data[6] is reinforcement_count
        current_salience = data[5]
        current_count = data[6]
        
        new_count = current_count + 1
        # Habituation decay: Salience grows logarithmically, scaled by habituation_rate
        new_salience = 1.0 + (policy.habituation_rate * math.log(1 + new_count))
        
        data[5] = new_salience
        data[6] = new_count
        
        EDGE_STRUCT.pack_into(self.mm, edge_offset, *data)
        
    def promote_edge(self, edge_idx: int, new_origin: str):
        edge_offset = self._get_edge_offset(edge_idx)
        data = list(EDGE_STRUCT.unpack_from(self.mm, edge_offset))
        
        o_int = EDGE_ORIGIN_MAP.get(new_origin, 0)
        prov_flags = data[3]
        
        # Clear old origin bits, set new origin
        r_int = prov_flags & 0xF
        new_flags = (o_int << 4) | r_int
        data[3] = new_flags
        
        EDGE_STRUCT.pack_into(self.mm, edge_offset, *data)
        
    def apoptosis(self, policy: GovernancePolicy = None) -> int:
        """Compost old, unpromoted hypothetical nodes to free up the lattice."""
        if policy is None:
            policy = GovernancePolicy()
            
        current_time_ns = time.time_ns()
        pruned_count = 0
        
        for idx in range(MAX_LATTICE_NODES):
            node_offset = self._get_node_offset(idx)
            ingested_at = struct.unpack_from("<Q", self.mm, node_offset + 8)[0]
            
            if ingested_at == 0:
                continue # Already empty
                
            age_ns = current_time_ns - ingested_at
            if age_ns < policy.prune_max_age_ns:
                continue
                
            incoming = self.get_incoming_edges(idx)
            if not incoming:
                continue
                
            # Check if strictly hypothetical
            all_hypothetical = all(e["origin"] == "Hypothetical" for e in incoming)
            if all_hypothetical:
                # In a full system we'd check resonance here using protect_high_resonance.
                # For now, if all are hypothetical and it's old, we compost it.
                struct.pack_into("<Q", self.mm, node_offset + 8, 0)
                pruned_count += 1
                
        return pruned_count

    def trace_lineage(self, start_node_id: int, max_depth: int = 3) -> dict:
        graph = {"nodes": {}, "edges": []}
        
        queue = [(start_node_id, 0)]
        visited = set([start_node_id])
        
        while queue:
            current_id, depth = queue.pop(0)
            
            node_data = NODE_STRUCT.unpack_from(self.mm, self._get_node_offset(current_id))
            if node_data[1] == 0:
                continue # Skip empty/pruned nodes
                
            graph["nodes"][current_id] = {
                "timestamps": {
                    "ingested_at": node_data[1],
                    "documented_at": node_data[2],
                    "valid_from": node_data[3],
                    "valid_until": node_data[4] if node_data[4] != NULL_IDX else None
                },
                "type": node_data[5],
                "payload": self.get_node_payload(current_id)
            }
            
            if depth >= max_depth:
                continue
                
            incoming = self.get_incoming_edges(current_id)
            for edge in incoming:
                source_id = edge["source"]
                graph["edges"].append({
                    "source": source_id, 
                    "target": current_id, 
                    "type": edge["type"],
                    "provenance": edge["provenance"],
                    "salience": edge["salience"]
                })
                
                if source_id not in visited:
                    visited.add(source_id)
                    queue.append((source_id, depth + 1))
                    
        return graph

    def flush(self):
        self.mm.flush()

    def close(self):
        self.flush()
        self.mm.close()
        self.file.close()
