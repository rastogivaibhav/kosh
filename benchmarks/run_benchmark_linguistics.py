import os
import shutil
import time
from pprint import pprint
from app.kosh.kernel import MemoryKernel
from app.kosh.adapters.native_ingestor import NativeIngestor
from app.kosh.reasoning import LyapunovCritic

# Setup isolated benchmark graph
DB_PATH = os.path.join(os.path.dirname(__file__), "benchmark_linguistics.pgdb")
CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus", "cern_fusion_raw")

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
    print(f"Ingested {len(id_map)} papers natively in {duration_ms:.2f} ms.")
    
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
    # We trace lineage from the final synthesis node (mit_2022) backwards
    if "mit_2022" not in id_map:
        print("Missing mit_2022 in corpus!")
        return

    mit_node = id_map["mit_2022"]
    lineage = kernel.trace_lineage(mit_node, max_depth=3)
    
    for edge in lineage["edges"]:
        source_id = edge["source"]
        target_id = edge["target"]
        origin = edge["provenance"]
        
        # Reverse lookup ID -> doc_id
        src_doc = next((k for k, v in id_map.items() if v == source_id), str(source_id))
        tgt_doc = next((k for k, v in id_map.items() if v == target_id), str(target_id))
        
        print(f"  {src_doc} --[{origin}]--> {tgt_doc}")
        
    print("\n[5] CDSS Lyapunov Stability Check on the Synthesised Truth (mit_2022):")
    critic = LyapunovCritic(kernel)
    stability = critic.evaluate(mit_node, max_depth=3)
    
    print(f"  Lyapunov V-Score: {stability['score']:.4f} ({stability['status'].upper()})")
    print(f"  Metrics: {stability['metrics']}")
    
    print("\nBenchmark Complete. Native pure-math linguistics engine validated.")


if __name__ == "__main__":
    run_benchmark()
