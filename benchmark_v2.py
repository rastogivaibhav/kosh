import os
import time
import random
from kosh.kernel import MemoryKernel

def main():
    db_path = "benchmark_v2.pgdb"
    
    if os.path.exists(db_path):
        os.remove(db_path)

    print("Starting v2 Benchmark: 1,000,000 Nodes (Advanced Provenance Bit-Packing)")
    
    # 1 million 72-byte nodes + 1 million 40-byte edges + 100MB heap payload
    # 72MB + 40MB + 100MB = ~212MB
    db = MemoryKernel(db_path, max_file_size=512 * 1024 * 1024)
    
    print("1. Inserting 1,000,000 nodes with complex provenance...")
    start_time = time.time()
    
    db.insert_node(event_type=0, payload={"msg": "root"})
    
    for i in range(1, 1_000_000):
        parent_id = i - 1
        
        # Alternate origins and roles to test bit packing
        origin = "Inferred" if i % 2 == 0 else "Observed"
        role = "Predictive" if i % 3 == 0 else "Mechanistic"
        
        db.insert_node(
            event_type=1, 
            payload={"idx": i, "data": "benchmark payload"}, 
            parent_id=parent_id,
            edge_origin=origin,
            edge_role=role
        )
        
        if i > 10 and random.random() < 0.1:
            random_parent = random.randint(0, i - 2)
            db.insert_edge(
                source_id=random_parent, 
                target_id=i, 
                edge_type=2,
                edge_origin="Hypothetical",
                edge_role="Analogical"
            )
            
    insert_time = time.time() - start_time
    print(f"Insertion complete in {insert_time:.2f} seconds ({(1_000_000 / insert_time):.0f} nodes/sec).")
    
    print("2. Benchmarking 3-Hop Traversal Latency (with bit unpacking)...")
    latencies = []
    sample_nodes = [random.randint(900_000, 999_999) for _ in range(100)]
    
    for node_id in sample_nodes:
        t0 = time.perf_counter()
        graph = db.trace_lineage(node_id, max_depth=3)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
        
        # Just sanity check the first one to ensure unpacking works
        if node_id == sample_nodes[0]:
            print("\nSample Graph Output (Provenance Unpacked):")
            for edge in graph["edges"]:
                print(f"  -> Edge from {edge['source']}: {edge['provenance']}")
            print("")
        
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    print(f"Average 3-hop traversal latency: {avg_latency:.4f} ms")
    print(f"Maximum 3-hop traversal latency: {max_latency:.4f} ms")
    
    if avg_latency < 50.0:
        print("\nSUCCESS! The v2 kernel maintained sub-50ms latency.")
    else:
        print("\nFAILED! Bit packing/unpacking caused >50ms latency.")
        
    db.close()

if __name__ == "__main__":
    main()
