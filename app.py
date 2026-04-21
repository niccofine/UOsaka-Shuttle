import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Shuttle Bus", layout="wide")

st.title("🚌 Shuttle Bus Timetable")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("buses.csv")
df["Time"] = pd.to_datetime(df["Time"])
df["Time"] = df["Time"].dt.tz_localize("Asia/Tokyo")
now = pd.Timestamp.utcnow()
now = now.tz_convert("Asia/Tokyo")
df["Time"] = df["Time"].apply(
    lambda t: now.normalize() + pd.Timedelta(hours=t.hour, minutes=t.minute)
)
df.loc[df["Time"] < now, "Time"] += pd.Timedelta(days=1)

# -----------------------------
# ROUTE + STOPS SELECTION
# -----------------------------
routes = df["Route"].unique()
route = st.selectbox("Route", routes)

stops = df[df["Route"] == route]["Stop"].unique()

col1, col2 = st.columns(2)

with col1:
    origin = st.selectbox("From", stops)

with col2:
    destination = st.selectbox("To", stops)

# -----------------------------
# FILTER FUTURE BUSES FROM ORIGIN
# -----------------------------
origin_df = df[
    (df["Route"] == route) &
    (df["Stop"] == origin) &
    (df["Time"] >= now)
].sort_values("Time")

next_buses = origin_df.drop_duplicates("BusNumber").reset_index(drop=True)

# -----------------------------
# SAFETY CHECK
# -----------------------------
if len(next_buses) == 0:
    st.warning("No upcoming buses from this stop.")
    st.stop()

# -----------------------------
# AUTO MODE: TAKE NEXT BUS
# -----------------------------
row = next_buses.iloc[0]

bus = row["BusNumber"]
dep_time = row["Time"]

minutes_left = int((dep_time - now).total_seconds() / 60)

# -----------------------------
# MAIN INFO DISPLAY
# -----------------------------
st.subheader(f"🚌 Next Bus: N. {bus}")

c1, c2, c3 = st.columns(3)

c1.metric("Departure", dep_time.strftime("%H:%M"))
c2.metric("Leaves in", f"{minutes_left} min")
c3.metric("Route", route)

st.divider()

# -----------------------------
# FULL ROUTE TIMELINE + ETA
# -----------------------------
full = df[
    (df["Route"] == route) &
    (df["BusNumber"] == bus)
].sort_values("StopOrder")

st.markdown("### 🧭 Trip timeline")

timeline = []

for r in full.itertuples():
    t = pd.to_datetime(r.Time)
    eta = int((t - now).total_seconds() / 60)

    if r.Stop == origin:
        tag = "🟢 FROM"
    elif r.Stop == destination:
        tag = "🔴 TO"
    else:
        tag = "➡️"

    timeline.append(
        f"{tag} **{r.Stop}** — {t.strftime('%H:%M')} ({eta} min)"
    )

st.write("\n".join(timeline))

st.divider()

import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import numpy as np

st.title("🚌 Live Transit (Simulation)")

# -----------------------------
# STOPS (fixed in code)
# -----------------------------
stops = {
    "Toyonaka": (135.455476, 34.805372),
    "Minoh": (135.491291, 34.823157),
    "Convention Center": (135.522847, 34.818302),
    "Engineering": (135.522947, 34.824184),
}

route_order = ["Toyonaka", "Minoh", "Convention Center", "Engineering"]

# -----------------------------
# OSRM ROUTE
# -----------------------------
coords = ";".join([f"{stops[s][0]},{stops[s][1]}" for s in route_order])

url = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"
data = requests.get(url).json()

route = data["routes"][0]["geometry"]["coordinates"]
path = [[lat, lon] for lon, lat in route]

# -----------------------------
# TIMETABLE (SIMULATED FROM CSV LOGIC)
# -----------------------------
df = pd.read_csv("buses.csv")
df["Time"] = pd.to_datetime(df["Time"])
df["Time"] = df["Time"].dt.tz_localize("Asia/Tokyo")
now = pd.Timestamp.utcnow()
now = now.tz_convert("Asia/Tokyo")
df["Time"] = df["Time"].apply(
    lambda t: now.normalize() + pd.Timedelta(hours=t.hour, minutes=t.minute)
)
df.loc[df["Time"] < now, "Time"] += pd.Timedelta(days=1)

# each bus = one departure time
buses = df.groupby("BusNumber").first().reset_index()

# -----------------------------
# INTERPOLATION FUNCTION
# -----------------------------
def interpolate(path, progress):
    progress = max(0, min(1, progress))
    idx = progress * (len(path) - 1)

    i0 = int(np.floor(idx))
    i1 = min(i0 + 1, len(path) - 1)

    t = idx - i0

    lat = path[i0][0] + (path[i1][0] - path[i0][0]) * t
    lon = path[i0][1] + (path[i1][1] - path[i0][1]) * t

    return [lat, lon]

# -----------------------------
# BUILD BUS POSITIONS (TRUE TIME)
# -----------------------------
bus_points = []

for _, bus in buses.iterrows():

    bus_id = bus["BusNumber"]
    dep_time = bus["Time"]

    # assume fixed travel duration (example: 20 min)
    arr_time = dep_time + pd.Timedelta(minutes=20)

    # hide buses not started yet
    if now < dep_time or now > arr_time:
        continue

    delta_total = (arr_time - dep_time).total_seconds()
    delta_now = (now - dep_time).total_seconds()
    
    progress = delta_now / delta_total if delta_total > 0 else 0
    progress = max(0, min(1, progress))

    pos = interpolate(path, progress)

    bus_points.append({
        "lat": pos[0],
        "lon": pos[1],
        "bus": str(bus_id),
        "time": str(dep_time),
    })

# -----------------------------
# LAYERS
# -----------------------------
route_layer = pdk.Layer(
    "PathLayer",
    data=[{"path": path}],
    get_path="path",
    get_width=5,
    get_color=[0, 100, 255],
)

bus_layer = pdk.Layer(
    "ScatterplotLayer",
    data=bus_points,
    get_position='[lon, lat]',
    get_radius=120,
    pickable=True,
    auto_highlight=True,
)

stop_layer = pdk.Layer(
    "ScatterplotLayer",
    data=[{"lat": v[1], "lon": v[0]} for v in stops.values()],
    get_position='[lon, lat]',
    get_radius=80,
    get_color=[255, 0, 0],
)

# -----------------------------
# CLICK INTERACTION
# -----------------------------
tooltip = {
    "html": "<b>Bus:</b> {bus}<br><b>Departure:</b> {time}",
    "style": {"backgroundColor": "black", "color": "white"},
}

# -----------------------------
# MAP
# -----------------------------
st.pydeck_chart(
    pdk.Deck(
        layers=[route_layer, stop_layer, bus_layer],
        initial_view_state=pdk.ViewState(
            latitude=np.mean([v[1] for v in stops.values()]),
            longitude=np.mean([v[0] for v in stops.values()]),
            zoom=13,
        ),
        tooltip=tooltip,
    )
)
