import streamlit as st

# ==============================
# 🚦 Smart Traffic & Route Predictor
# ==============================

st.set_page_config(
    page_title="🚦 Smart Traffic & Route Predictor",
    page_icon="🚗",
    layout="centered"
)

# === CSS Styling ===
st.markdown("""
<style>
body {
    background: #f8f9fa;
    color: #333;
}
.main-container {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    text-align: center;
}
h1 {
    color: #0077b6;
    text-align: center;
    font-size: 2.5rem;
}
h2 {
    color: #00b4d8;
}
.team-box {
    margin-top: 20px;
    background: #e3f2fd;
    padding: 1rem;
    border-radius: 15px;
}
.footer {
    text-align: center;
    margin-top: 50px;
    color: #777;
}
</style>
""", unsafe_allow_html=True)

# === Main Layout ===
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("🚗 Smart Traffic & Route Predictor")
st.write("""
Welcome to the **Smart Traffic & Route Predictor** — a modern AI-powered web application 
that predicts **traffic flow** and helps you visualize **optimal driving routes** with live data.
""")

st.markdown("### 🌟 Key Features")
st.markdown("""
✅ **City Traffic Prediction:**  
Get real-time traffic predictions using live weather data and ML models.

✅ **Route Traffic Prediction:**  
Find the best routes between locations with estimated distance and travel time.

✅ **Analytics Dashboard (coming next):**  
Visualize traffic insights, trends, and performance metrics.
""")

st.markdown("---")

st.markdown("### 💡 How to Use")
st.markdown("""
Use the **sidebar** on the left to switch between:
- 🏙️ *City Traffic Prediction*  
- 🗺️ *Route Traffic Prediction*  
- 📊 *Analytics View*
""")

st.markdown("---")

st.markdown("### 👨‍💻 Developed By")
st.markdown("""
<div class="team-box">
<b>Nitesh & Team</b>  
Department of Information Science & Engineering  
BMS Institute of Technology & Management, Bengaluru
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">© 2025 Smart Traffic & Route Predictor | All Rights Reserved 🚀</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
