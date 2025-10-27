# 🧪 AI-Lab — Cloud Demos (Pratik N Das)
**Product Manager | AI, Data & SaaS | Building smarter digital ecosystems**

This lab is a cloud-first portfolio of **hands-on AI demos** — built to run on web platforms (Streamlit Cloud, Hugging Face Spaces, and Vercel). No local setup required.

## ☁️ Live Demos (publish & paste links)
| Demo | What it shows | Platform | Link |
|------|----------------|----------|------|
| ETA Predictor | Classical ML (regression) + metrics | Streamlit Cloud | (https://ai-lab-fufemwfinsyvc9tmasg6wh.streamlit.app) |
| Cargo Claims Classifier | Lightweight NLP classification | Hugging Face Spaces (Gradio) | (https://huggingface.co/spaces/pratikndas/AI_Lab)|
| Freight RAG Assistant | Retrieval + templated LLM answer | Hugging Face Spaces (Gradio) | _add link_ |
| Lead Scoring API | Simple scoring API (FastAPI) | Vercel Serverless | _add link ( /api/score )_ |

> Tip: After deployment, update the table with your live URLs.

---

## 🔧 Deploy (no local run needed)
- **Streamlit Cloud (ETA Predictor)**: connect repo → pick `/demos/eta-streamlit/app.py`
- **Hugging Face Spaces (Gradio apps)**: new Space → Gradio template → upload `/demos/claims-gradio/app.py` or `/demos/rag-space/app.py`
- **Vercel (FastAPI)**: import repo → it auto-detects `api/index.py` (Python runtime via `vercel.json`)

---

## 📘 Documentation
- [`docs/RAG_Architecture.md`](docs/RAG_Architecture.md)
- [`docs/Model_Evaluation_Framework.md`](docs/Model_Evaluation_Framework.md)
- [`docs/AI_Product_Guardrails.md`](docs/AI_Product_Guardrails.md)

---

## 🧠 Why this convinces recruiters
- **Interactive demos** (not just code) prove product + engineering collaboration
- **Clear AI architecture & evaluation docs** show maturity
- **Serverless/API example** shows platform thinking

---

## 🖼️ Portfolio Site (GitHub Pages)
A simple landing page is included under `/site`. Enable **GitHub Pages → deploy from `/site`** and use it as your one-click portfolio hub.
