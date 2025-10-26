from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Lead Scoring API (Demo)")

class Lead(BaseModel):
    budget: float
    is_enterprise: bool = False
    touches: int = 0
    days_to_first_reply: float = 5.0

@app.get("/")
def root():
    return {"ok": True, "message": "Lead Scoring API demo. POST /api/score with lead JSON."}

@app.post("/score")
def score(lead: Lead):
    # Simple heuristic model (demo only)
    score = (lead.budget/100000) + (0.3 if lead.is_enterprise else 0) + (0.02*lead.touches) - (0.01*lead.days_to_first_reply)
    score = max(0.0, min(1.0, score))
    return {"win_probability": round(score,3)}