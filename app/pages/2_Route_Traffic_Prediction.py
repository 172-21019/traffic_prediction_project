import streamlit as st
import requests
import folium

# =========================================
# 🚗 Live Route Traffic (TomTom API - Manual Refresh)
# =========================================

st.set_page_config(page_title="🗺️ Live Route Traffic", layout="centered")

# === TOMTOM API KEY ===
TOMTOM_API_KEY = "vVzbNRaFcTDVcNFbUY3agB3O8Srt7LKw"

# === PAGE TITLE ===
st.title("🗺️ Live Route Traffic (TomTom API)")
st.write("View **real-time traffic congestion** between any two Bengaluru locations 🚦")

# === CSS Styling ===
st.markdown("""
<style>
h1, h2, h3 {text-align: center; color: #00b4d8;}
.stButton>button {
    background-color: #00b4d8;
    color: white;
    border-radius: 10px;
    width: 100%;
    height: 3em;
}
.stButton>button:hover { background-color: #0077b6; }
.clear-btn > button {
    background-color: #6c757d !important;
}
.clear-btn > button:hover {
    background-color: #495057 !important;
}
.refresh-btn > button {
    background-color: #ffb703 !important;
    color: black !important;
}
.refresh-btn > button:hover {
    background-color: #f48c06 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# === SESSION STATE INIT ===
if "route" not in st.session_state:
    st.session_state.route = None
if "map_html" not in st.session_state:
    st.session_state.map_html = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "route_points" not in st.session_state:
    st.session_state.route_points = None
if "src" not in st.session_state:
    st.session_state.src = None
if "dest" not in st.session_state:
    st.session_state.dest = None


# === Helper Functions ===
def geocode(location):
    """Convert location name into coordinates using TomTom API."""
    try:
        url = f"https://api.tomtom.com/search/2/geocode/{location}.json?key={TOMTOM_API_KEY}"
        data = requests.get(url).json()
        if data.get("results"):
            return data["results"][0]["position"]
    except:
        pass
    return None


def get_route(src, dest):
    """Fetch the route between two coordinates."""
    url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{src['lat']},{src['lon']}:{dest['lat']},{dest['lon']}/json?traffic=true&key={TOMTOM_API_KEY}"
    )
    res = requests.get(url).json()
    if "routes" not in res:
        return None
    return res["routes"][0]


def get_traffic(points):
    """Fetch congestion levels at sampled route points."""
    data = []
    checkpoints = points[::max(1, len(points)//6)]
    for p in checkpoints:
        lat, lon = p["latitude"], p["longitude"]
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&unit=KMPH&key={TOMTOM_API_KEY}"
        resp = requests.get(url).json().get("flowSegmentData", {})
        if not resp:
            continue
        curr, free = resp["currentSpeed"], resp["freeFlowSpeed"]
        if free == 0:
            continue
        congestion = round((1 - curr / free) * 100, 1)
        if congestion < 25:
            color, label = "green", "🟢 Low"
        elif congestion < 60:
            color, label = "orange", "🟠 Moderate"
        else:
            color, label = "red", "🔴 High"
        data.append((lat, lon, color, label, curr, free))
    return data


def build_map(src, dest, points, traffic_data):
    """Create folium map HTML."""
    m = folium.Map(location=(src["lat"], src["lon"]), zoom_start=12)
    folium.Marker((src["lat"], src["lon"]), popup="Source", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker((dest["lat"], dest["lon"]), popup="Destination", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([(p["latitude"], p["longitude"]) for p in points], color="blue", weight=6).add_to(m)

    for lat, lon, color, label, curr, free in traffic_data:
        folium.CircleMarker(
            location=(lat, lon), radius=8, color=color,
            fill=True, fill_opacity=0.9,
            popup=f"{label} ({curr}/{free} km/h)"
        ).add_to(m)

    return m._repr_html_()


# === UI ===
if st.session_state.route is None:
    with st.form("route_form"):
        src_input = st.text_input("Enter Source (e.g., Silk Board, Bengaluru)")
        dest_input = st.text_input("Enter Destination (e.g., Yelahanka, Bengaluru)")
        submit = st.form_submit_button("🚗 Get Live Route")

        if submit:
            if not src_input or not dest_input:
                st.warning("⚠️ Please enter both source and destination.")
            else:
                src = geocode(src_input)
                dest = geocode(dest_input)
                if not src or not dest:
                    st.error("❌ Location not found. Try again.")
                else:
                    with st.spinner("Fetching route and live traffic..."):
                        route = get_route(src, dest)
                        if not route:
                            st.error("❌ Could not find route.")
                        else:
                            points = route["legs"][0]["points"]
                            dist = route["summary"]["lengthInMeters"] / 1000
                            time_min = route["summary"]["travelTimeInSeconds"] / 60
                            traffic = get_traffic(points)
                            map_html = build_map(src, dest, points, traffic)

                            # Save to session
                            st.session_state.route = (src_input, dest_input)
                            st.session_state.map_html = map_html
                            st.session_state.summary = [t[3] for t in traffic]
                            st.session_state.route_points = points
                            st.session_state.src = src
                            st.session_state.dest = dest

                            st.success(f"✅ Route from {src_input} → {dest_input}")
                            st.metric("📏 Distance (km)", f"{dist:.2f}")
                            st.metric("⏱️ Duration (min)", f"{time_min:.1f}")


# === DISPLAY MAP ===
if st.session_state.map_html:
    src_input, dest_input = st.session_state.route
    st.markdown(f"## 🗺️ {src_input} → {dest_input}")
    st.components.v1.html(st.session_state.map_html, height=500)

    st.markdown("### 📊 Congestion Summary")
    st.write(" → ".join(st.session_state.summary))

    # --- Refresh & Clear Buttons ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="refresh-btn">', unsafe_allow_html=True)
        if st.button("🔄 Refresh Live Data"):
            with st.spinner("Fetching latest congestion levels..."):
                traffic = get_traffic(st.session_state.route_points)
                if traffic:
                    st.session_state.map_html = build_map(
                        st.session_state.src, st.session_state.dest, st.session_state.route_points, traffic
                    )
                    st.session_state.summary = [t[3] for t in traffic]
                    st.success("✅ Traffic data updated!")
                    st.rerun()
                else:
                    st.warning("⚠️ Could not fetch updated traffic data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear & Choose New Route"):
            for key in ["route", "map_html", "summary", "route_points", "src", "dest"]:
                st.session_state[key] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr><center>Developed by <b>Nitesh & Team 🚀 | BMSIT</b></center>", unsafe_allow_html=True)
