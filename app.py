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
def route_stops(r):
    return list(df[df["Route"] == r].sort_values("StopOrder")["Stop"].unique())


def on_route_change():
    stops = route_stops(st.session_state["route"])
    old_from = st.session_state.get("origin")
    old_to = st.session_state.get("destination")
    new_from, new_to = old_to, old_from
    if new_from not in stops or new_to not in stops or new_from == new_to:
        new_from, new_to = stops[0], stops[-1]
    st.session_state["origin"] = new_from
    st.session_state["destination"] = new_to


routes = df["Route"].unique()
route = st.selectbox("Route", routes, key="route", on_change=on_route_change)

stops = route_stops(route)

# Defaults: opposite ends; repair state if it is invalid for this route
if st.session_state.get("origin") not in stops:
    st.session_state["origin"] = stops[0]
if st.session_state.get("destination") not in stops:
    st.session_state["destination"] = stops[-1]
if st.session_state["origin"] == st.session_state["destination"]:
    st.session_state["destination"] = stops[-1] if st.session_state["origin"] != stops[-1] else stops[0]

col1, col2 = st.columns(2)

# Each selector excludes the other's current choice, so they can never match
with col1:
    origin = st.selectbox(
        "From", [s for s in stops if s != st.session_state["destination"]], key="origin"
    )

with col2:
    destination = st.selectbox(
        "To", [s for s in stops if s != st.session_state["origin"]], key="destination"
    )

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

# -----------------------------
# NEXT BUSES PREVIEW
# -----------------------------
st.markdown("### ⏭️ Next buses from this stop")

for i in range(min(3, len(next_buses))):
    b = next_buses.iloc[i]
    m = int((b["Time"] - now).total_seconds() / 60)
    st.write(f"🚌 Bus {b['BusNumber']} — {b['Time'].strftime('%H:%M')} ({m} min)")

st.divider()
