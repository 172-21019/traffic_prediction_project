import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="📊 Model Analytics Dashboard", layout="wide")

st.title("📊 Model Analytics Dashboard")

st.markdown("""
This dashboard shows how different ML models performed during training.  
It helps visualize their **accuracy, error metrics, and comparison** to choose the best one.
""")

# === Load previous results if available ===
try:
    results_df = pd.read_csv("model_results.csv")
    best_model_name = results_df.loc[results_df['R2'].idxmax(), 'Model']
    st.success(f"🏆 Best Model: **{best_model_name}**")
except:
    st.warning("⚠️ Model results file not found. Please run `main.py` once to generate training results.")
    st.stop()

# === Show raw table ===
st.subheader("📋 Model Performance Summary")
st.dataframe(results_df.style.highlight_max(axis=0, color="lightgreen"))

# === Plot R² comparison ===
st.subheader("📈 R² Score Comparison")

fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x="Model", y="R2", data=results_df, ax=ax)
ax.set_title("Model R² Scores", fontsize=14)
ax.set_ylabel("R² Score")
st.pyplot(fig)

# === Plot MAE and MSE ===
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.barplot(x="Model", y="MAE", data=results_df, ax=ax)
    ax.set_title("Mean Absolute Error (MAE)")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.barplot(x="Model", y="MSE", data=results_df, ax=ax)
    ax.set_title("Mean Squared Error (MSE)")
    st.pyplot(fig)

st.markdown("<hr><center>Developed by <b>Nitesh & Team 🚀 | BMSIT</b></center>", unsafe_allow_html=True)
