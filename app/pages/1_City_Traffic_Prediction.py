import streamlit as st
import joblib
import numpy as np
import pandas as pd
import requests
from datetime import datetime
import folium
from streamlit_folium import st_folium
import math
from dotenv import load_dotenv
import os

# === Load environment variables ===
load_dotenv()

# === Page Config ===
st.set_page_config(page_title="🏙️ City Traffic Prediction", layout="centered")
st.title("🏙️ City Traffic Prediction (Live Data)")

# === Load Models & Assets ===
try:
    model = joblib.load("best_ml_model.pkl")
    cls_model = joblib.load("best_cls_model.pkl")
    le = joblib.load("label_encoder.pkl")
    feature_columns = joblib.load("feature_columns.pkl")
except Exception:
    st.error("❌ Models or feature_columns.pkl not found. Run main.py first to train models.")
    st.stop()

# === CSS Styling ===
st.markdown("""
<style>
body {
    background: #f8f9fa;
    color: #333;
}
.main {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    margin-top: 25px;
}
h1 {
    text-align: center;
    color: #0077b6;
    font-size: 2.3rem;
    margin-bottom: 10px;
}
h2, h3 {
    text-align: center;
    color: #00b4d8;
}
.stButton>button {
    background-color: #00b4d8;
    color: white;
    border-radius: 10px;
    width: 100%;
    height: 3em;
    font-weight: 600;
    border: none;
}
.stButton>button:hover { background-color: #0077b6; }
.refresh-button>button {
    background-color: #6c757d;
    color: white;
    border-radius: 10px;
    width: 100%;
    height: 3em;
}
.refresh-button>button:hover { background-color: #495057; }
.tip {
    font-size: 1.1rem;
    font-weight: 500;
    text-align: center;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}
.low-tip { background-color: #d4edda; color: #155724; }
.moderate-tip { background-color: #fff3cd; color: #856404; }
.high-tip { background-color: #f8d7da; color: #721c24; }
.refresh-info {
    text-align: center;
    color: #555;
    margin-top: 10px;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# === API Keys ===
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
TOMTOM_KEY = os.getenv("TOMTOM_API_KEY", "")

# === Maintain State ===
if "city" not in st.session_state:
    st.session_state.city = "Bangalore"
if "last_update" not in st.session_state:
    st.session_state.last_update = None
if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None

# === User Input ===
st.markdown('<div class="main">', unsafe_allow_html=True)
city = st.text_input("🏙️ Enter your city name:", st.session_state.city)
st.session_state.city = city    # Store for refresh reuse

col1, col2 = st.columns(2)

# === Main Predict Button ===
with col1:
    predict_clicked = st.button("🔍 Get Live Data & Predict")

# === Manual Refresh Button ===
with col2:
    refresh_clicked = st.button("🔄 Refresh Data", key="refresh_btn")

# === Prediction Logic (used by both buttons) ===
def get_live_prediction(city):
    if not WEATHER_API_KEY:
        st.warning("⚠️ WEATHER_API_KEY not found in .env. Set it for live data.")
        st.stop()

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()

    if data.get("cod") == 200:
        temp = data["main"]["temp"]
        clouds = data["clouds"]["all"]
        rain = data.get("rain", {}).get("1h", 0)
        snow = data.get("snow", {}).get("1h", 0)
        now = datetime.now()
        month = now.month
        weekday = now.weekday()
        hour = now.hour

        # Cyclical time encoding
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        # Prepare DataFrame
        feature_dict = {
            'temp': temp,
            'rain_1h': rain,
            'snow_1h': snow,
            'clouds_all': clouds,
            'hour_sin': hour_sin,
            'hour_cos': hour_cos,
            'weekday': weekday,
            'month': month
        }
        features = pd.DataFrame([feature_dict])[feature_columns]

        # Predict traffic & congestion
        traffic_pred = model.predict(features)[0]
        cls_pred = cls_model.predict(features)
        congestion_label = le.inverse_transform(cls_pred)[0]

        st.session_state.prediction_data = {
            "temp": temp,
            "clouds": clouds,
            "traffic_pred": int(traffic_pred),
            "congestion": congestion_label
        }
        st.session_state.last_update = now.strftime("%H:%M:%S")
    else:
        st.error("⚠️ City not found. Please try again.")

# === TOMTOM GEOCODING FUNCTION ===
def geocode_place(place_name, key=TOMTOM_KEY):
    """
    Convert a place name into (latitude, longitude) using TomTom Geocoding API.
    Restrict results to India to improve accuracy.
    """
    try:
        url = f"https://api.tomtom.com/search/2/geocode/{requests.utils.quote(place_name)}.json"
        params = {
            "key": key,
            "limit": 1,
            "countrySet": "IN"  # Restrict search to India 🇮🇳
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()

        if data.get("results"):
            lat = data["results"][0]["position"]["lat"]
            lon = data["results"][0]["position"]["lon"]
            st.info(f"📍 {place_name} → {lat:.4f}, {lon:.4f}")
            return f"{lat},{lon}"
        else:
            st.error(f"⚠️ Could not find coordinates for: {place_name}")
            return None
    except Exception as e:
        st.error(f"Error geocoding '{place_name}': {e}")
        return None


# === TOMTOM LIVE ROUTE & INCIDENT HELPERS ===
def get_route_coords(origin, destination, key=TOMTOM_KEY):
    """Get route coordinates from TomTom between origin and destination."""
    try:
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin}:{destination}/json?key={key}&traffic=true"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        coords = []
        for leg in data["routes"][0]["legs"]:
            for point in leg["points"]:
                coords.append([point["latitude"], point["longitude"]])
        return coords
    except Exception as e:
        st.error(f"Error fetching route: {e}")
        return []

def route_bbox(coords, pad_deg=0.01):
    """Create a bounding box around a list of [lat, lon] coordinates"""
    lats = [p[0] for p in coords]
    lons = [p[1] for p in coords]
    min_lat, max_lat = min(lats) - pad_deg, max(lats) + pad_deg
    min_lon, max_lon = min(lons) - pad_deg, max(lons) + pad_deg
    return min_lon, min_lat, max_lon, max_lat

def get_incidents_for_bbox(bbox, key=TOMTOM_KEY):
    """Fetch live incidents in the given bounding box"""
    try:
        min_lon, min_lat, max_lon, max_lat = bbox
        url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
        params = {"bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}", "key": key}
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching incidents: {e}")
        return {}

def draw_route_and_incidents(route_coords, incidents_json):
    """Draw route and incidents on a Folium map"""
    if not route_coords:
        st.warning("No route found.")
        return None

    mid = route_coords[len(route_coords)//2]
    m = folium.Map(location=mid, zoom_start=12)
    folium.PolyLine(route_coords, weight=6, color="blue", opacity=0.8).add_to(m)

    incidents = incidents_json.get("incidents", incidents_json.get("features", []))
    for inc in incidents:
        try:
            geom = inc.get("geometry", {})
            coords = geom.get("coordinates")
            if coords:
                lat, lon = coords[1], coords[0]
            else:
                continue
            props = inc.get("properties", {})
            desc = ""
            if props.get("events"):
                desc = props["events"][0].get("description", "")
            else:
                desc = props.get("description", "Unknown incident")
            delay = props.get("delay", 0)
            popup = f"{desc}<br>Delay: {int(delay)//60} mins" if delay else desc
            folium.Marker(
                [lat, lon],
                popup=popup,
                icon=folium.Icon(color="red", icon="exclamation-sign")
            ).add_to(m)
        except Exception:
            continue
    return m

# === Trigger Prediction or Refresh ===
if predict_clicked or refresh_clicked:
    get_live_prediction(st.session_state.city)

# === Display Prediction Results ===
if st.session_state.prediction_data:
    data = st.session_state.prediction_data
    st.metric("🌡️ Temperature (°C)", f"{data['temp']:.1f}")
    st.metric("☁️ Cloud Coverage (%)", f"{data['clouds']}%")
    st.metric("🚗 Predicted Traffic", f"{data['traffic_pred']} vehicles/hour")

    color_map = {
        "Low": ("🟢 Low (Smooth Flow)", "✅ Roads are clear. Great time to travel!", "low-tip"),
        "Moderate": ("🟠 Moderate (Medium Flow)", "⚠️ Some congestion — plan ahead.", "moderate-tip"),
        "High": ("🔴 High (Heavy Congestion)", "🚨 Avoid if possible — peak hour traffic!", "high-tip")
    }

    congestion_text, travel_tip, css_class = color_map.get(data["congestion"], ("❓ Unknown", "", ""))
    st.markdown(f"### 🚦 Congestion Level: {congestion_text}")
    st.markdown(f'<div class="tip {css_class}">{travel_tip}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="refresh-info">🕐 Last Updated: {st.session_state.last_update}</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# === LIVE ROUTE EVENTS SECTION ===
st.markdown("<hr>", unsafe_allow_html=True)
st.header("🛰️ Live Events Along Route")

col1, col2 = st.columns(2)
with col1:
    source_place = st.text_input("Enter Source Place:", "BMS Institute of Technology, Yelahanka")
with col2:
    destination_place = st.text_input("Enter Destination Place:", "Majestic, Bengaluru")

if st.button("🚗 Show Live Route Events"):
    if not TOMTOM_KEY:
        st.error("TomTom API key not found! Please add it to your .env file.")
    else:
        source_coords = geocode_place(source_place)
        dest_coords = geocode_place(destination_place)

        if source_coords and dest_coords:
            route_coords = get_route_coords(source_coords, dest_coords)
            if route_coords:
                bbox = route_bbox(route_coords, pad_deg=0.015)
                incidents = get_incidents_for_bbox(bbox)
                map_obj = draw_route_and_incidents(route_coords, incidents)
                if map_obj:
                    st_folium(map_obj, width=800, height=500)
            else:
                st.error("Could not get route. Please check the locations.")
        else:
            st.warning("Could not find one or both of the locations.")

st.markdown("<hr><center>Developed by <b>Nitesh & Team 🚀 | BMSIT</b></center>", unsafe_allow_html=True)
