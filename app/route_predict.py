# route_predict.py
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import time

load_dotenv()
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")  # falls back to empty if not set

st.set_page_config(page_title="🗺️ Live Route Traffic", layout="centered")
st.title("🗺️ Live Route Traffic (TomTom API - Multi-Point Flow)")

# User inputs
source = st.text_input("Enter Source (e.g., BMSIT College, Yelahanka)")
destination = st.text_input("Enter Destination (e.g., Majestic, Bangalore)")

if st.button("🚗 Show Live Route Traffic"):
    if not TOMTOM_API_KEY:
        st.error("TOMTOM_API_KEY not found in environment (.env). Add TOMTOM_API_KEY to .env or set variable.")
    else:
        try:
            # helper to geocode
            def geocode(location):
                url = f"https://api.tomtom.com/search/2/geocode/{location}.json?key={TOMTOM_API_KEY}"
                r = requests.get(url)
                data = r.json()
                return data["results"][0]["position"] if data.get("results") else None

            src = geocode(source)
            dest = geocode(destination)
            if not src or not dest:
                st.error("❌ Could not geocode one or both locations. Try more specific names.")
            else:
                src_coords = (src["lat"], src["lon"])
                dest_coords = (dest["lat"], dest["lon"])

                # Get route
                route_url = f"https://api.tomtom.com/routing/1/calculateRoute/{src['lat']},{src['lon']}:{dest['lat']},{dest['lon']}/json?traffic=true&key={TOMTOM_API_KEY}"
                route_data = requests.get(route_url).json()
                if "routes" not in route_data:
                    st.error("❌ Could not fetch route.")
                else:
                    route_points = route_data["routes"][0]["legs"][0]["points"]
                    distance = route_data["routes"][0]["summary"]["lengthInMeters"] / 1000.0
                    duration = route_data["routes"][0]["summary"]["travelTimeInSeconds"] / 60.0

                    st.success(f"✅ Route found: {source} → {destination}")
                    st.metric("📏 Distance (km)", f"{distance:.2f}")
                    st.metric("⏱️ Estimated Duration (min)", f"{duration:.1f}")

                    # Build map & polyline
                    m = folium.Map(location=src_coords, zoom_start=12)
                    folium.Marker(src_coords, popup="Source", icon=folium.Icon(color="green")).add_to(m)
                    folium.Marker(dest_coords, popup="Destination", icon=folium.Icon(color="red")).add_to(m)
                    folium.PolyLine([(p["latitude"], p["longitude"]) for p in route_points], color="blue", weight=4, opacity=0.6).add_to(m)

                    st.markdown("### 🚦 Live Traffic Flow Along Route")
                    # sample points evenly: aim 5–7 checks
                    n_checks = min(7, max(1, len(route_points)//20))
                    step = max(1, len(route_points)//(n_checks))
                    sample_points = route_points[::step][:7]

                    traffic_levels = []
                    for p in sample_points:
                        lat, lon = p["latitude"], p["longitude"]
                        # try with 1000m radius first
                        flow_url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/1000/json?point={lat},{lon}&unit=KMPH&key={TOMTOM_API_KEY}"
                        resp = requests.get(flow_url)
                        try:
                            data = resp.json()
                        except Exception:
                            data = {}

                        # fallback: if no data, try smaller radius 500 then 2000
                        if "flowSegmentData" not in data:
                            for rad in (500, 2000):
                                flow_url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/{rad}/json?point={lat},{lon}&unit=KMPH&key={TOMTOM_API_KEY}"
                                resp = requests.get(flow_url)
                                try:
                                    data = resp.json()
                                except Exception:
                                    data = {}
                                if "flowSegmentData" in data:
                                    break

                        if "flowSegmentData" in data:
                            flow = data["flowSegmentData"]
                            curr, free = flow.get("currentSpeed"), flow.get("freeFlowSpeed")
                            if curr is None or free is None or free == 0:
                                label = "❌ No Speed Data"
                                color = "gray"
                            else:
                                congestion = round((1 - curr/free) * 100, 1)
                                if congestion < 25:
                                    color, label = "green", "🟢 Low"
                                elif congestion < 60:
                                    color, label = "orange", "🟠 Moderate"
                                else:
                                    color, label = "red", "🔴 High"

                                folium.CircleMarker(location=(lat, lon), radius=8, color=color, fill=True, fill_opacity=0.8, popup=f"{label} ({curr}/{free} km/h)").add_to(m)
                                traffic_levels.append(f"{label} ({curr}/{free} km/h)")
                        else:
                            # No flow data even after fallbacks
                            folium.CircleMarker(location=(lat, lon), radius=6, color="gray", fill=True, fill_opacity=0.5, popup="No data").add_to(m)
                            traffic_levels.append("No Data")

                        time.sleep(0.2)

                    st_folium(m, width=700, height=500)
                    st.markdown("### 📊 Route Traffic Summary")
                    st.write(" → ".join(traffic_levels))

        except Exception as e:
            st.error(f"❌ Error: {e}")
