import os
import pypdf
import json
from kosh.kernel import MemoryKernel

def main():
    print("--- Kosh Legal AI Agent Simulation ---")
    
    # Initialize Kosh Database
    db_path = "legal_memory.pgdb"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = MemoryKernel(db_path, max_file_size=512 * 1024 * 1024)

    # 1. AI Agent reads the PDF (Observation Phase)
    pdf_path = r"C:\Users\vrast\OneDrive\Apps\Documents\llm-kosh-cart\pdfs\-0___jonew__judis__10166.pdf"
    print(f"\n[Agent] Reading document: {os.path.basename(pdf_path)}")
    
    # We simulate the LLM extracting distinct facts from the raw text
    # (In reality, the text goes to the LLM, and the LLM calls the MCP tool)
    
    print("\n[Agent] Structuring facts and storing in Kosh...")
    
    # Fact 1: The Case Title
    fact1_id = db.insert_node(
        event_type=0, 
        payload={"fact": "Case is BALAJI RAGHAVAN Vs. S.P. ANAND", "source": "Page 1 Header"},
        edge_origin="Observed",
        edge_role="Contextual"
    )
    
    # Fact 2: The Bench
    fact2_id = db.insert_node(
        event_type=0,
        payload={"fact": "Bench includes AHMADI A.M. (CJ), KULDIP SINGH, JEEVAN REDDY, SINGH N.P, AHMAD SAGHIR S."},
        parent_id=fact1_id,
        edge_origin="Observed",
        edge_role="Mechanistic"
    )

    # 2. AI Agent reasons about the facts (Hypothesis Phase)
    # The LLM notices a 5-judge bench including the Chief Justice and forms a hypothesis.
    print("[Agent] Reasoning about the bench structure...")
    hypo_id = db.insert_node(
        event_type=1,
        payload={"thought": "This is a 5-judge bench including the CJI. Hypothesis: This involves a substantial question of Constitutional Law.", "confidence": 0.8},
        parent_id=fact2_id,
        edge_origin="Hypothetical",
        edge_role="Predictive"
    )

    # 3. Memory Retrieval Phase (User asks a question)
    print("\n--- User Query: 'Why did you classify this as a Constitutional case?' ---")
    print("[Kosh] Executing causal trace_lineage from the hypothesis node...\n")
    
    # The database traces backwards from the hypothesis to the observed root cause
    graph_trace = db.trace_lineage(hypo_id, max_depth=3)
    
    print(json.dumps(graph_trace, indent=2))
    
    db.close()

if __name__ == "__main__":
    main()
