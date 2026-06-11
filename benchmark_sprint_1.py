import os
import time
import random
import shutil
from provenance_graph_db import MemoryKernel

def main():
    db_path = "benchmark.pgdb"
    
    # Clean up old run
    if os.path.exists(db_path):
        os.remove(db_path)

    print("Starting Sprint 1 Benchmark: 1,000,000 Nodes (Python Mmap)")
    
    # Initialize DB (512MB for 1M nodes and edges + heap)
    db = MemoryKernel(db_path, max_file_size=512 * 1024 * 1024)
    
    print("1. Inserting 1,000,000 nodes...")
    start_time = time.time()
    
    # We create a deep chain to ensure 3-hop traverses are meaningful
    # Node 0 is root.
    db.insert_node(event_type=0, payload={"msg": "root"})
    
    for i in range(1, 1_000_000):
        # Every node derives from the previous node to create a massive chain,
        # plus some random connections to simulate complexity.
        parent_id = i - 1
        db.insert_node(event_type=1, payload={"idx": i, "data": "benchmark payload"}, parent_id=parent_id)
        
        # Add a random second edge for 10% of nodes to simulate branching
        if i > 10 and random.random() < 0.1:
            random_parent = random.randint(0, i - 2)
            db.insert_edge(source_id=random_parent, target_id=i, edge_type=2)
            
    insert_time = time.time() - start_time
    print(f"Insertion complete in {insert_time:.2f} seconds ({(1_000_000 / insert_time):.0f} nodes/sec).")
    
    print("2. Benchmarking 3-Hop Traversal Latency...")
    # Sample 100 random leaf nodes near the end
    latencies = []
    sample_nodes = [random.randint(900_000, 999_999) for _ in range(100)]
    
    for node_id in sample_nodes:
        t0 = time.perf_counter()
        graph = db.trace_lineage(node_id, max_depth=3)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000) # Convert to ms
        
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    print(f"Average 3-hop traversal latency: {avg_latency:.4f} ms")
    print(f"Maximum 3-hop traversal latency: {max_latency:.4f} ms")
    
    if avg_latency < 50.0:
        print("\nSUCCESS! The pure Python mmap engine beat the 50ms kill-switch constraint.")
    else:
        print("\nFAILED! Latency is >50ms. A Rust core is required.")
        
    db.close()

if __name__ == "__main__":
    main()
