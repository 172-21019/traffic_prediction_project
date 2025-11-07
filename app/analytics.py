import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Model Performance & Traffic Analytics")

# Load results
try:
    results = pd.read_csv("model_results.csv")
    st.subheader("🚀 Regression Model Results")
    st.dataframe(results)

    st.bar_chart(results.set_index("Model")["R2"])

    st.subheader("📈 Accuracy Comparison")
    fig, ax = plt.subplots()
    ax.bar(results["Model"], results["R2"], edgecolor='black')
    ax.set_ylabel("R2 Score")
    ax.set_xlabel("Model Name")
    ax.set_title("Model Performance (Higher is Better)")
    st.pyplot(fig)

except Exception as e:
    st.warning("⚠️ Run main.py first to generate model_results.csv")
    st.error(e)
