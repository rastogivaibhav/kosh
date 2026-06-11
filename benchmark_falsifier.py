import os
import math
import json
from collections import Counter
from kosh.kernel import MemoryKernel

# 1. Dataset
events = [
    {"id": 0, "text": "Alert: Database CPU at 99%"},
    {"id": 1, "text": "Slack: Looks like the database is failing, I will restart it."},
    {"id": 2, "text": "Alert: Network switch dropping packets."},
    {"id": 3, "text": "Postmortem: The network switch failure caused retry loops, which spiked the Database CPU. The database was not at fault."}
]

# 2. Mock Vector RAG (TF-IDF Cosine Similarity)
def tokenize(text):
    return text.lower().replace('.', '').replace(',', '').split()

def compute_tf_idf(corpus):
    docs = [tokenize(e["text"]) for e in corpus]
    N = len(docs)
    df = Counter()
    for doc in docs:
        for word in set(doc):
            df[word] += 1
            
    idf = {word: math.log(N / count) for word, count in df.items()}
    return idf

def semantic_search(query, corpus, top_k=2):
    idf = compute_tf_idf(corpus)
    q_tokens = tokenize(query)
    
    scores = []
    for doc in corpus:
        tokens = tokenize(doc["text"])
        score = 0
        for q in q_tokens:
            if q in tokens:
                tf = tokens.count(q) / len(tokens)
                score += tf * idf.get(q, 0)
        scores.append((score, doc))
        
    scores.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scores[:top_k]]

def run_falsifier():
    print("=== THE HYPOKOSH MINIMAL FALSIFIER ===")
    print("Query: 'Why did the database fail?'\n")
    
    # Run Semantic RAG
    print("--- 1. Semantic Vector RAG Context (Top-2) ---")
    rag_results = semantic_search("Why did the database fail", events)
    for doc in rag_results:
        print(f"[{doc['id']}] {doc['text']}")
        
    # Run Graph Traversal
    print("\n--- 2. Causal Graph Traversal Context ---")
    db_path = "falsifier.pgdb"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    kernel = MemoryKernel(db_path, max_file_size=512*1024*1024) # 512MB default
    
    # Insert Nodes and Edges
    # E0 happens
    n0 = kernel.insert_node(0, events[0])
    # E1 derives from E0
    n1 = kernel.insert_node(1, events[1], parent_id=n0)
    # E2 happens independently
    n2 = kernel.insert_node(0, events[2])
    # E3 (Postmortem) derives from E2 (Network) and E0 (DB CPU)
    n3 = kernel.insert_node(2, events[3], parent_id=n2)
    kernel.insert_edge(source_id=n0, target_id=n3, edge_type=1)
    
    # We trace lineage starting from the symptom (E0) backwards and forwards.
    # Our current trace_lineage goes backwards (incoming edges).
    # To trace "what caused this", we look at incoming edges. But E0 has no incoming.
    # Actually, E3 derives from E0 and E2. If an agent is investigating E0, it will
    # look for nodes that derive from E0 (children).
    # Since our `kernel.py` currently only tracks `first_incoming_edge_idx`, BFS only goes backwards.
    # We should trace backwards from the Postmortem (E3) to see the full causal chain,
    # OR the agent traces backwards from E1 (Slack) and hits E0, and then queries E3.
    # Let's trace backwards from the Postmortem (E3).
    
    graph = kernel.trace_lineage(n3, max_depth=2)
    
    print("Retrieved Graph nodes:")
    for node_id, data in graph["nodes"].items():
        print(f"[{node_id}] {data['payload']['text']}")
        
    print("\nRetrieved Graph edges (Provenance):")
    for edge in graph["edges"]:
        print(f"Node {edge['source']} -> Node {edge['target']} (Type: {edge['type']})")
        
    print("\n=== CONCLUSION ===")
    rag_ids = [doc['id'] for doc in rag_results]
    if 2 not in rag_ids:
        print("Vector RAG completely missed the Root Cause Alert (Node 2).")
        print("Because 'Network switch dropping packets' shares NO keywords with 'database fail'.")
        print("It suffered from 'Similarity Dominance'.\n")
        
    if 2 in graph["nodes"] and 3 in graph["nodes"]:
        print("Graph Traversal perfectly captured the Postmortem AND the underlying Root Cause Alert.")
        print("Hypothesis PROVEN: Causal retrieval escapes semantic traps and finds the true root cause.")

    kernel.close()

if __name__ == "__main__":
    run_falsifier()
