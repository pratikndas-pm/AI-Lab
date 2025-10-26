import gradio as gr

CATEGORIES = {
    "Damage": ["damaged","wet","broken","dents","packaging"],
    "Delay": ["delayed","congestion","late","schedule","missed"],
    "Loss": ["missing","lost","theft","not found","stolen"],
    "Documentation": ["paperwork","invoice","bl","customs","document"]
}

def classify_claim(text):
    t = text.lower()
    scores = {k:0 for k in CATEGORIES}
    for k, kws in CATEGORIES.items():
        for kw in kws:
            if kw in t:
                scores[k]+=1
    label = max(scores, key=scores.get)
    return label, scores

demo = gr.Interface(fn=classify_claim, inputs=gr.Textbox(lines=6, placeholder="Paste claim description..."), outputs=[gr.Label(num_top_classes=4), gr.JSON()], title="Cargo Claims Classifier (Demo)")
demo.launch()