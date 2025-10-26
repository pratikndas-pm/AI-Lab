# RAG Architecture (High-Level)
1) **Ingest** small domain texts (carriers, policies, FAQs)
2) **Index** as embeddings → vector store (FAISS/Chroma)
3) **Retrieve** top-k passages per query
4) **Generate** answer with grounded context
5) **Evaluate**: EM/semantic match, latency p95, cost/1k tokens
6) **Guardrails**: citations required, safe output filters, fallback answers