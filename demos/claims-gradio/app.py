import gradio as gr

CATEGORIES = {
    "Damage": ["damaged","wet","broken","dents","packaging"],
    "Delay": ["delayed","congestion","late","schedule","missed"],
    "Loss": ["missing","lost","theft","not found","stolen"],
    "Documentation": ["paperwork","invoice","bl","customs","document"]
}

def classify_claim(text):
    t = (text or "").lower()
    scores = {k:0 for k in CATEGORIES}
    for k, kws in CATEGORIES.items():
        for kw in kws:
            if kw in t:
                scores[k] += 1
    # pick the label with the highest score (ties go to the first max)
    label = max(scores, key=scores.get) if any(scores.values()) else "Uncertain"
    return label, scores

EXAMPLES = [
    ["Container was damaged and packaging broken; cargo inside was wet."],
    ["Shipment delayed due to heavy port congestion and missed vessel schedule."],
    ["Two boxes missing from manifest, cargo possibly lost or stolen during transit."],
    ["Incorrect invoice and missing BL documents caused customs delay."],
    ["Shipment delayed and some packages broken due to poor handling."],
    ["Customer reported issue."]
]

TABLE_MD = """
### 🧪 Test Cases

| Test Case         | Example Input Text                                                               | Expected Category                                                            |
| ----------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 🧱 Damage         | `Container was damaged and packaging broken; cargo inside was wet.`              | **Damage**                                                                   |
| ⏰ Delay          | `Shipment delayed due to heavy port congestion and missed vessel schedule.`       | **Delay**                                                                    |
| 📦 Loss           | `Two boxes missing from manifest, cargo possibly lost or stolen during transit.` | **Loss**                                                                     |
| 📄 Documentation  | `Incorrect invoice and missing BL documents caused customs delay.`               | **Documentation**                                                            |
| Mixed / Edge case | `Shipment delayed and some packages broken due to poor handling.`                | **Damage (or Delay)** — classifier counts keywords, whichever dominates wins |
| Empty / neutral   | `Customer reported issue.`                                                       | No strong category (may default to whichever has 0 > others)                 |
"""

with gr.Blocks(title="Cargo Claims Classifier (Demo)") as demo:
    gr.Markdown(
        "# 📄 Cargo Claims Classifier\n"
        "_Lightweight NLP demo that classifies claim descriptions into Damage, Delay, Loss, or Documentation._\n\n"
        "Paste a claim description or click an example below. The app shows a predicted category and the keyword hit counts used for the decision."
    )

    inp = gr.Textbox(lines=6, label="Claim Description", placeholder="Paste claim description…")
    out_label = gr.Label(label="Predicted Category", num_top_classes=4)
    out_json = gr.JSON(label="Keyword Scores")

    gr.Examples(examples=EXAMPLES, inputs=inp, label="Quick Test Inputs")
    gr.Markdown(TABLE_MD)

    btn = gr.Button("Classify")
    btn.click(fn=classify_claim, inputs=inp, outputs=[out_label, out_json])

demo.launch()
