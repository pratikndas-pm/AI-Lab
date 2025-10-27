import gradio as gr

def score_lead(budget, is_enterprise, touches, days_to_first_reply):
    s = (budget/100000.0) + (0.30 if is_enterprise else 0.0) + (0.02*touches) - (0.01*days_to_first_reply)
    s = max(0.0, min(1.0, s))
    reasons = []
    reasons.append("high budget signals stronger intent" if budget >= 50000 else "moderate budget supports conversion" if budget >= 20000 else "lower budget reduces likelihood")
    reasons.append("enterprise account uplift applied (+0.30)" if is_enterprise else "non-enterprise (no uplift)")
    reasons.append("healthy engagement (touches ≥ 4)" if touches >= 4 else "some engagement (2–3 touches)" if touches >= 2 else "low engagement (touches < 2)")
    reasons.append("fast first response (≤ 2 days)" if days_to_first_reply <= 2 else "acceptable first response (≤ 5 days)" if days_to_first_reply <= 5 else "slow first response (> 5 days)")
    explanation = f"Predicted win probability: {s:.0%}. Signals considered: " + "; ".join(reasons) + "."
    return round(s, 3), explanation, {
        "budget": budget,
        "is_enterprise": is_enterprise,
        "touches": touches,
        "days_to_first_reply": days_to_first_reply
    }

with gr.Blocks(title="Lead Scoring (Demo)") as demo:
    gr.Markdown("# 📈 Lead Scoring (Demo)\nLightweight scoring with an explanation — no setup, runs in the browser.")
    with gr.Row():
        budget = gr.Slider(0, 100000, value=30000, step=1000, label="Budget (USD)")
        is_ent = gr.Checkbox(value=True, label="Enterprise account?")
    with gr.Row():
        touches = gr.Slider(0, 10, value=3, step=1, label="Sales touches")
        days = gr.Slider(0, 20, value=1, step=1, label="Days to first reply")
    btn = gr.Button("Score Lead")
    prob = gr.Number(label="Win probability (0–1)")
    expl = gr.Textbox(label="Explanation")
    echo = gr.JSON(label="Inputs")
    btn.click(fn=score_lead, inputs=[budget, is_ent, touches, days], outputs=[prob, expl, echo])

    gr.Markdown("""### 🔗 Programmatic use (auto)
Click the **Use via API** button at the top of this Space to copy a ready-made `requests` snippet
that calls this demo and returns JSON (no server setup required).
""")

demo.launch()
