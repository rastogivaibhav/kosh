import json
import os
from mcp.server.fastmcp import FastMCP
from kosh.kernel import MemoryKernel

# Initialize FastMCP Server
mcp = FastMCP("ProvenanceGraphDB")

# Global singleton for the DB kernel in the MCP context
db_path = os.environ.get("PGDB_PATH", "agent_memory_v2.pgdb")
kernel = MemoryKernel(db_path)

@mcp.tool()
def insert_memory(
    event_type_id: int, 
    payload_json: str, 
    parent_node_id: int = None,
    edge_origin: str = "Observed",
    edge_role: str = "Causal"
) -> str:
    """
    Insert a new memory event into the deterministic graph DB.
    
    Args:
        event_type_id: Integer representing the type of event (0: Observation, 1: Thought, 2: Action).
        payload_json: A JSON string containing the memory payload.
        parent_node_id: Optional ID of the node this memory derives from.
        edge_origin: Enforce provenance origin ["Observed", "Discovered", "Inferred", "Reinforced", "Hypothetical"].
        edge_role: Enforce provenance role ["Mechanistic", "Compressed", "Analogical", "Predictive", "Causal"].
    """
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON payload."})
        
    try:
        node_id = kernel.insert_node(
            event_type=event_type_id, 
            payload=payload, 
            parent_id=parent_node_id,
            edge_origin=edge_origin,
            edge_role=edge_role
        )
        return json.dumps({"status": "success", "node_id": node_id})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def insert_edge(
    source_node_id: int,
    target_node_id: int,
    edge_type_id: int = 1,
    edge_origin: str = "Observed",
    edge_role: str = "Causal"
) -> str:
    """
    Draw a causal link between two existing memory nodes without creating a new node.
    """
    try:
        kernel.insert_edge(
            source_id=source_node_id,
            target_id=target_node_id,
            edge_type=edge_type_id,
            edge_origin=edge_origin,
            edge_role=edge_role
        )
        return json.dumps({"status": "success"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def trace_memory_lineage(node_id: int, max_depth: int = 3) -> str:
    """
    Trace the exact lineage and provenance of a specific memory node backwards through time.
    Returns explicit EdgeOrigins and EdgeRoles so you know if a link was 'Hypothetical' vs 'Observed'.
    """
    try:
        graph = kernel.trace_lineage(start_node_id=node_id, max_depth=max_depth)
        return json.dumps({"status": "success", "graph": graph}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    print(f"Starting ProvenanceGraphDB v2 MCP Server (DB: {db_path})", flush=True)
    mcp.run()
