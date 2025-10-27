
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI(
    title="Lead Scoring API (Demo)",
    description="Serverless FastAPI on Vercel. POST /api/score with lead JSON to get win probability and explanation.",
    version="1.0.0",
)

class Lead(BaseModel):
    budget: float
    is_enterprise: bool = False
    touches: int = 0
    days_to_first_reply: float = 5.0

def compute_score(lead: Lead) -> Dict[str, float]:
    score = (lead.budget / 100000.0) + (0.30 if lead.is_enterprise else 0.0) + (0.02 * lead.touches) - (0.01 * lead.days_to_first_reply)
    score = max(0.0, min(1.0, score))
    return {"win_probability": round(score, 3)}

def build_explanation(lead: Lead, score: float) -> str:
    reasons = []
    if lead.budget >= 50000: reasons.append("high budget signals stronger intent")
    elif lead.budget >= 20000: reasons.append("moderate budget supports conversion")
    else: reasons.append("lower budget reduces likelihood")
    if lead.is_enterprise: reasons.append("enterprise account uplift applied (+0.30)")
    else: reasons.append("non‑enterprise (no uplift)")
    if lead.touches >= 4: reasons.append("healthy engagement (touches ≥ 4)")
    elif lead.touches >= 2: reasons.append("some engagement (2–3 touches)")
    else: reasons.append("low engagement (touches < 2)")
    if lead.days_to_first_reply <= 2: reasons.append("fast first response (≤ 2 days)")
    elif lead.days_to_first_reply <= 5: reasons.append("acceptable first response (≤ 5 days)")
    else: reasons.append("slow first response (> 5 days)")
    return f"Predicted win probability: {score:.0%}. " + "Signals considered: " + "; ".join(reasons) + "."

@app.get("/api")
def root():
    return {"ok": True, "message": "Lead Scoring API demo. POST /api/score with lead JSON."}

@app.post("/api/score")
def score(lead: Lead):
    s = compute_score(lead)["win_probability"]
    explanation = build_explanation(lead, s)
    return {"win_probability": s, "explanation": explanation, "inputs": lead.dict()}
