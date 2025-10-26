import gradio as gr, numpy as np
from collections import Counter

DOCS = [
    "Freight ETA depends on distance, stops, carrier reliability, and port congestion.",
    "Insurance claims triage can be accelerated by categorizing claim types and extracting key entities.",
    "Route optimization can reduce CO2 emissions by selecting efficient carriers and schedules."
]

VOCAB = sorted(set(" ".join(DOCS).lower().split()))
IDX = {w:i for i,w in enumerate(VOCAB)}

def vec(text):
    c = Counter(text.lower().split()); v = np.zeros(len(VOCAB))
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
    answer = f"Based on context: {' | '.join(ctx)}. Suggest: enrich with distance, stops, carrier reliability, congestion, and seasonality; use historical patterns for better ETA/decisions."
    return answer, "\n- " + "\n- ".join(ctx)

demo = gr.Interface(fn=qa, inputs=gr.Textbox(placeholder="Ask a freight/logistics question..."), outputs=[gr.Textbox(label="Answer"), gr.Textbox(label="Retrieved Context")], title="Freight RAG Assistant (Demo)")
demo.launch()