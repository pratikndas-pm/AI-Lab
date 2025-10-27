import gradio as gr, numpy as np
from collections import Counter

# --- In-memory documents ---
DOCS = [
    "Freight ETA depends on distance, stops, carrier reliability, and port congestion.",
    "Insurance claims triage can be accelerated by categorizing claim types and extracting key entities.",
    "Route optimization can reduce CO2 emissions by selecting efficient carriers and schedules."
]

VOCAB = sorted(set(" ".join(DOCS).lower().split()))
IDX = {w:i for i,w in enumerate(VOCAB)}

def vec(text):
    c = Counter(text.lower().split())
    v = np.zeros(len(VOCAB))
    for w,n in c.items():
        if w in IDX: v[IDX[w]] = n
    return v

DOCV = [vec(d) for d in DOCS]

def cosine(a,b):
    if np.linalg.norm(a)==0 or np.linalg.norm(b)==0: return 0.0
    return float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))

def retrieve(q, topk=2):
    qv = vec(q)
    scored = sorted([(cosine(qv, dv), d) for dv,d in zip(DOCV, DOCS)], reverse=True, key=lambda x:x[0])
    return [d for s,d in scored[:topk]]

def qa(query):
    ctx = retrieve(query)
    answer = (
        f"Based on context: {' | '.join(ctx)}.\n\n"
        f"Suggest: enrich with distance, stops, carrier reliability, congestion, and seasonality; "
        f"use historical patterns for better ETA/decisions."
    )
    return answer, "\n- " + "\n- ".join(ctx)

# --- Predefined example test data ---
EXAMPLES = [
    ["How can I improve freight ETA accuracy?"],
    ["How can insurance claims be processed faster?"],
    ["What's the best way to reduce CO2 emissions in shipping routes?"],
    ["What factors delay container shipments?"],
    ["How to optimize routes and speed up claim approvals?"],
    ["Who won the football match yesterday?"]
]

# --- Gradio Interface ---
with gr.Blocks(title="Freight RAG Assistant (Demo)") as demo:
    gr.Markdown("""
    # 🚢 Freight RAG Assistant  
    _Retrieval-Augmented Generation demo for freight & logistics use cases._  

    Ask a question related to shipping, ETA, claims, or optimization — the app retrieves relevant context and generates a templated AI-style answer.

    ---
    🧠 **Try these sample questions:**
    - How can I improve freight ETA accuracy?
    - How can insurance claims be processed faster?
    - What’s the best way to reduce CO₂ emissions in shipping routes?
    - What factors delay container shipments?
    - How to optimize routes and speed up claim approvals?
    - Who won the football match yesterday? (unrelated test)
    ---
    """)

    inp = gr.Textbox(label="Your Question", placeholder="Ask a freight/logistics question…")
    out1 = gr.Textbox(label="AI Answer")
    out2 = gr.Textbox(label="Retrieved Context")

    gr.Examples(examples=EXAMPLES, inputs=inp, label="🧩 Quick test examples")
    demo_btn = gr.Button("Generate Answer")
    demo_btn.click(fn=qa, inputs=inp, outputs=[out1, out2])

demo.launch()
