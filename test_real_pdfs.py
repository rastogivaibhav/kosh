import os
import time
import glob
import pypdf
import random
from kosh.kernel import MemoryKernel

def main():
    pdf_dir = r"C:\Users\vrast\OneDrive\Apps\Documents\llm-kosh-cart\pdfs"
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))[:100] # Limit to first 100 for test
    
    if not pdf_files:
        print(f"No PDFs found in {pdf_dir}")
        return

    print(f"Found {len(pdf_files)} PDFs for the benchmark.")
    
    # 1. Parsing Phase
    print("\n--- Phase 1: PDF Extraction (Python Bottleneck) ---")
    start_parse = time.time()
    
    extracted_text = []
    total_file_bytes = 0
    
    for pdf_path in pdf_files:
        try:
            total_file_bytes += os.path.getsize(pdf_path)
            reader = pypdf.PdfReader(pdf_path)
            doc_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    doc_text += text + "\n"
            extracted_text.append(doc_text)
        except Exception as e:
            # Some PDFs might be encrypted or malformed
            pass

    parse_time = time.time() - start_parse
    mb_processed = total_file_bytes / (1024 * 1024)
    print(f"Extracted text from {len(pdf_files)} PDFs ({mb_processed:.2f} MB)")
    print(f"PDF Extraction Time: {parse_time:.2f} seconds")
    
    # 2. Chunking
    chunk_size = 500
    chunks = []
    for doc in extracted_text:
        for i in range(0, len(doc), chunk_size):
            chunks.append(doc[i:i+chunk_size])
            
    print(f"Total structured facts/chunks generated: {len(chunks)}")
    
    # 3. Database Insertion Phase
    print("\n--- Phase 2: Kosh Database Ingestion ---")
    db_path = "real_pdfs.pgdb"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    kernel = MemoryKernel(db_path, max_file_size=512 * 1024 * 1024)
    
    start_insert = time.time()
    
    node_ids = []
    for i, chunk in enumerate(chunks):
        n_id = kernel.insert_node(
            event_type=0, 
            payload={"text": chunk},
            edge_origin="Observed",
            edge_role="Mechanistic"
        )
        node_ids.append(n_id)
        
        # Simulate an LLM drawing causal edges between 10% of chunks
        if i > 0 and random.random() < 0.1:
            random_parent = random.choice(node_ids[:-1])
            kernel.insert_edge(
                source_id=random_parent,
                target_id=n_id,
                edge_type=1,
                edge_origin="Inferred",
                edge_role="Causal"
            )

    insert_time = time.time() - start_insert
    print(f"Kosh DB Insertion Time: {insert_time:.4f} seconds")
    print(f"Kosh DB Speed: {(len(chunks)/insert_time):.0f} nodes/sec")
    
    # 4. Extrapolation to 5GB
    print("\n--- 5GB Extrapolation ---")
    gb_target = 5 * 1024 # 5120 MB
    multiplier = gb_target / mb_processed if mb_processed > 0 else 0
    
    est_parse_hours = (parse_time * multiplier) / 3600
    est_insert_seconds = (insert_time * multiplier)
    
    print(f"To ingest exactly 5GB of PDFs:")
    print(f"1. PDF Parsing Time (Python/CPU bound): ~{est_parse_hours:.2f} HOURS")
    print(f"2. Kosh DB Insertion Time (mmap bound): ~{est_insert_seconds:.2f} SECONDS")
    
    kernel.close()

if __name__ == "__main__":
    main()
