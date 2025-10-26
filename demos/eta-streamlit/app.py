import streamlit as st
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

st.set_page_config(page_title="ETA Predictor", page_icon="⏱")
st.title("⏱ ETA Predictor — Freight ML (Demo)")

st.write("Upload a CSV or use synthetic data to predict ETA (hours). Columns: distance_km, stops, carrier_rating, port_congestion, season.")

use_sample = st.toggle("Use sample synthetic data", value=True)

if use_sample:
    np.random.seed(42)
    N=400
    distance_km = np.random.uniform(200, 12000, N)
    stops = np.random.randint(0, 6, N)
    carrier_rating = np.random.uniform(3.0, 5.0, N)
    port_congestion = np.random.uniform(0, 1, N)
    season = np.random.choice([0,1,2,3], N)
    eta_hours = distance_km/30 + stops*8 + (5-carrier_rating)*10 + port_congestion*36 + season*6 + np.random.normal(0, 12, N)
    df = pd.DataFrame(dict(distance_km=distance_km,stops=stops,carrier_rating=carrier_rating,port_congestion=port_congestion,season=season,eta_hours=eta_hours))
else:
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f: df = pd.read_csv(f)
    else: st.stop()

features = df.drop(columns=[c for c in df.columns if c.lower().startswith("eta")], errors="ignore")
target = df[[c for c in df.columns if c.lower().startswith("eta")]].iloc[:,0] if any(c.lower().startswith("eta") for c in df.columns) else None

# Train simple model
model = RandomForestRegressor(n_estimators=120, random_state=7)
if target is not None:
    model.fit(features, target)
    pred = model.predict(features)
    mae = mean_absolute_error(target, pred)
    st.metric("MAE (in-sample)", f"{mae:.2f} hrs")
else:
    model.fit(features, np.zeros(len(features)))
    pred = model.predict(features)

st.subheader("Preview")
st.dataframe(features.head())

# What-if prediction
st.subheader("What-if Scenario")
col1, col2 = st.columns(2)
with col1:
    distance_km = st.slider("Distance (km)", 200, 12000, 3000, 100)
    stops = st.slider("Stops", 0, 6, 2, 1)
    season = st.selectbox("Season", [0,1,2,3], index=2)
with col2:
    carrier_rating = st.slider("Carrier Rating", 3.0, 5.0, 4.3, 0.1)
    port_congestion = st.slider("Port Congestion", 0.0, 1.0, 0.3, 0.05)

x = pd.DataFrame([dict(distance_km=distance_km,stops=stops,carrier_rating=carrier_rating,port_congestion=port_congestion,season=season)])
eta_pred = model.predict(x)[0]
st.success(f"Estimated ETA: **{eta_pred:.1f} hours**")