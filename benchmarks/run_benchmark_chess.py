import os
import time
from pprint import pprint
from kosh.kernel import MemoryKernel
from kosh.adapters.native_ingestor import NativeIngestor
from kosh.reasoning import LyapunovCritic

# Setup isolated benchmark graph
DB_PATH = os.path.join(os.path.dirname(__file__), "benchmark_chess.pgdb")
CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus", "chess_raw")

def run_benchmark():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    print("\n[1] Initializing Kosh MemoryKernel ($O(1)$ spatial substrate)...")
    kernel = MemoryKernel(DB_PATH)
    
    print(f"\n[2] Native Ingestion of Multidisciplinary Raw Text from {CORPUS_DIR}...")
    ingestor = NativeIngestor(kernel)
    start_ns = time.perf_counter_ns()
    
    id_map = ingestor.ingest_directory(CORPUS_DIR)
    
    end_ns = time.perf_counter_ns()
    duration_ms = (end_ns - start_ns) / 1e6
    print(f"Ingested {len(id_map)} variations natively in {duration_ms:.2f} ms.")
    
    print("\n[3] Synthesized Node Data (Auto-scored via kosh.linguistics):")
    for doc_id, node_id in id_map.items():
        payload = kernel.get_node_payload(node_id)
        print(f"\nDocument: {doc_id} (Node {node_id})")
        print(f"  Status:       {payload['status']}")
        print(f"  Unusualness:  {payload.get('unusualness', 0):.4f}")
        print(f"  Coherence:    {payload.get('coherence', 0):.4f}")
        print(f"  Abstraction:  {payload.get('abstraction', 0):.4f}")
        print(f"  Resonance:    {payload.get('resonance', 0):.4f}")
        
    print("\n[4] Topological Edge Wiring (Auto-extracted from raw causal verbs):")
    # We trace lineage from the final synthesis node backwards
    if "alphazero_2017" not in id_map:
        print("Missing alphazero_2017 in corpus!")
        return

    final_node = id_map["alphazero_2017"]
    lineage = kernel.trace_lineage(final_node, max_depth=3)
    
    for edge in lineage["edges"]:
        source_id = edge["source"]
        target_id = edge["target"]
        origin = edge["provenance"]
        
        # Reverse lookup ID -> doc_id
        src_doc = next((k for k, v in id_map.items() if v == source_id), str(source_id))
        tgt_doc = next((k for k, v in id_map.items() if v == target_id), str(target_id))
        
        print(f"  {src_doc} --[{origin}]--> {tgt_doc}")
        
    print("\n[5] CDSS Lyapunov Stability Check on the Synthesised Truth (alphazero_2017):")
    critic = LyapunovCritic(kernel)
    stability = critic.evaluate(final_node, max_depth=3)
    
    print(f"  Lyapunov V-Score: {stability['score']:.4f} ({stability['status'].upper()})")
    print(f"  Metrics: {stability['metrics']}")
    
    print("\nBenchmark Complete. Chess moves successfully evaluated independently using linguistic CDSS.")


if __name__ == "__main__":
    run_benchmark()
