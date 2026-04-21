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

# -----------------------------
# NEXT BUSES PREVIEW
# -----------------------------
st.markdown("### ⏭️ Next buses from this stop")

for i in range(min(3, len(next_buses))):
    b = next_buses.iloc[i]
    m = int((b["Time"] - now).total_seconds() / 60)
    st.write(f"🚌 Bus {b['BusNumber']} — {b['Time'].strftime('%H:%M')} ({m} min)")

st.divider()
