import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Shuttle Bus", page_icon=":material/directions_bus:", layout="centered")

# -----------------------------
# ICONS
# -----------------------------
def icon(name, size=18):
    paths = {
        "bus": '<path d="M8 6v6"/><path d="M15 6v6"/><path d="M2 12h19.6"/><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/><circle cx="7" cy="18" r="2"/><path d="M9 18h5"/><circle cx="16" cy="18" r="2"/>',
        "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "timer": '<line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/>',
        "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
        "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
        "flag": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/>',
        "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
        "list": '<line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/>',
        "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    }
    return (
        f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths[name]}</svg>'
    )


def html(s):
    # Single-line HTML so Markdown never treats it as a code block
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def fmt_minutes(m):
    if m <= 0:
        return "Now"
    if m < 60:
        return f"{m} min"
    return f"{m // 60} h {m % 60:02d} min"


# -----------------------------
# STYLE
# -----------------------------
st.markdown(
    """
<style>
:root {
  --accent: #2563eb;
  --accent-soft: rgba(37, 99, 235, .12);
  --ok: #16a34a;
  --bad: #dc2626;
  --surface: rgba(128, 128, 128, .08);
  --border: rgba(128, 128, 128, .25);
  --muted: rgba(128, 128, 128, .95);
}
.block-container { max-width: 760px; padding-top: 2rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }
.ic { vertical-align: -3px; flex: none; }

.app-head { display: flex; align-items: center; gap: .75rem; margin-bottom: 1.25rem; }
.app-head .logo { width: 44px; height: 44px; border-radius: 12px; background: var(--accent);
  color: #fff; display: flex; align-items: center; justify-content: center; }
.app-head h1 { font-size: 1.5rem; line-height: 1.2; margin: 0; padding: 0; }
.app-head p { margin: 0; color: var(--muted); font-size: .85rem; }

.st-key-hero { border: 1px solid var(--border) !important; background: var(--surface);
  border-radius: 16px !important; padding: 1rem 1.25rem !important; margin: 1rem 0; }
.st-key-hero [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .5rem; }
.st-key-hero [data-testid="stColumn"] { min-width: 0 !important; }
.st-key-hero button { border-radius: 10px; }
.st-key-nbs button { justify-content: flex-start; border-radius: 12px; padding: .7rem 1rem; }
.st-key-nbs button[kind="primary"] { background: var(--accent-soft); color: inherit;
  border: 1px solid var(--accent); }
.st-key-nbs [data-testid="stElementContainer"] { margin-bottom: -.5rem; }
.top { display: flex; justify-content: space-between; align-items: center;
  gap: .5rem; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; gap: .35rem; background: var(--accent-soft);
  color: var(--accent); font-weight: 600; font-size: .8rem; padding: .25rem .65rem; border-radius: 999px; }
.st-key-hero .big { font-size: 3rem; font-weight: 700; line-height: 1.1; margin: .6rem 0 .1rem;
  font-variant-numeric: tabular-nums; }
.st-key-hero .sub { color: var(--muted); font-size: .9rem; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; margin-top: 1rem; }
.stat { border-top: 1px solid var(--border); padding-top: .75rem; }
.stat .lbl { color: var(--muted); font-size: .75rem; display: flex; align-items: center; gap: .3rem; }
.stat .val { font-size: 1.1rem; font-weight: 600; margin-top: .15rem; }

.section { display: flex; align-items: center; gap: .5rem; font-weight: 600;
  font-size: 1.05rem; margin: 1.75rem 0 .75rem; }

.tl { position: relative; margin: 0; padding: 0; list-style: none; }
.tl li { position: relative; display: flex; align-items: center; justify-content: space-between;
  gap: .75rem; padding: .55rem 0 .55rem 2rem; }
.tl li::before { content: ""; position: absolute; left: 7px; top: 0; bottom: 0; width: 2px;
  background: var(--border); }
.tl li:first-child::before { top: 50%; }
.tl li:last-child::before { bottom: 50%; }
.tl li.active::before { background: var(--accent); }
.tl li.active:first-child::before, .tl li.active:last-child::before { background: var(--accent); }
.tl li::after { content: ""; position: absolute; left: 2px; top: 50%; width: 12px; height: 12px;
  margin-top: -6px; border-radius: 50%; background: var(--surface); border: 2px solid var(--border);
  box-sizing: border-box; }
.tl li.active::after { border-color: var(--accent); background: var(--accent); }
.tl li.from::after { border-color: var(--ok); background: var(--ok); width: 16px; height: 16px;
  left: 0; margin-top: -8px; }
.tl li.to::after { border-color: var(--bad); background: var(--bad); width: 16px; height: 16px;
  left: 0; margin-top: -8px; }
.tl li.dim { opacity: .5; }
.tl .name { font-weight: 500; display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.tl .tag { font-size: .65rem; font-weight: 700; letter-spacing: .04em; padding: .1rem .45rem; border-radius: 6px; color: #fff; }
.tl .tag.f { background: var(--ok); }
.tl .tag.t { background: var(--bad); }
.tl .when { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.tl .when small { display: block; color: var(--muted); font-size: .72rem; }

.nb { display: flex; align-items: center; justify-content: space-between; gap: .75rem;
  border: 1px solid var(--border); background: var(--surface); border-radius: 12px;
  padding: .75rem 1rem; margin-bottom: .5rem; }
.nb .l { display: flex; align-items: center; gap: .75rem; }
.nb .t { font-size: 1.15rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.nb .r { text-align: right; font-size: .85rem; color: var(--muted); }
.nb .r b { color: inherit; font-weight: 600; display: block; }
.note { display: flex; gap: .6rem; align-items: flex-start; border: 1px solid var(--border);
  border-radius: 12px; padding: .75rem 1rem; background: var(--surface); margin: 1rem 0; }

@media (max-width: 600px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
  .st-key-hero .big { font-size: 2.4rem; }
  .stats { gap: .5rem; }
  .stat .val { font-size: 1rem; }
  .app-head h1 { font-size: 1.25rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

html(f"""
<div class="app-head">
  <div class="logo">{icon("bus", 24)}</div>
  <div><h1>Shuttle Bus</h1><p>Live timetable &middot; Asia/Tokyo</p></div>
</div>
""")

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
route = st.selectbox(
    ":material/route: Route", routes, key="route", on_change=on_route_change
)

stops = route_stops(route)

if st.session_state.get("origin") not in stops:
    st.session_state["origin"] = stops[0]
if st.session_state.get("destination") not in stops:
    st.session_state["destination"] = stops[-1]
if st.session_state["origin"] == st.session_state["destination"]:
    st.session_state["destination"] = stops[-1] if st.session_state["origin"] != stops[-1] else stops[0]

col1, col2 = st.columns(2)

with col1:
    origin = st.selectbox(
        ":material/trip_origin: From", [s for s in stops if s != st.session_state["destination"]],
        key="origin",
    )

with col2:
    destination = st.selectbox(
        ":material/location_on: To", [s for s in stops if s != st.session_state["origin"]],
        key="destination",
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
    html(f'<div class="note">{icon("alert", 20)}<div>No upcoming buses from this stop.</div></div>')
    st.stop()

order = {s: i for i, s in enumerate(stops)}
direction_ok = order[origin] < order[destination]
if not direction_ok:
    html(
        f'<div class="note">{icon("alert", 20)}<div>This route does not travel from '
        f'<b>{origin}</b> to <b>{destination}</b>. Try swapping the route.</div></div>'
    )


def arrival_at_destination(bus_no):
    m = df[(df["Route"] == route) & (df["BusNumber"] == bus_no) & (df["Stop"] == destination)]
    return m["Time"].iloc[0] if len(m) else None


# -----------------------------
# SELECTED BUS (HERO) + NAVIGATION
# -----------------------------
ctx = (route, origin)
if st.session_state.get("sel_ctx") != ctx:
    st.session_state["sel_ctx"] = ctx
    st.session_state["sel"] = 0
sel = min(st.session_state.get("sel", 0), len(next_buses) - 1)
st.session_state["sel"] = sel


def go(i):
    st.session_state["sel"] = i


row = next_buses.iloc[sel]
bus = row["BusNumber"]
dep_time = row["Time"]
minutes_left = int((dep_time - now).total_seconds() / 60)
arr = arrival_at_destination(bus) if direction_ok else None
duration = fmt_minutes(int((arr - dep_time).total_seconds() / 60)) if arr is not None else "–"
arr_txt = arr.strftime("%H:%M") if arr is not None else "–"
label = "Next departure" if sel == 0 else "Departure"

with st.container(border=True, key="hero"):
    nav_prev, nav_now, nav_next = st.columns([1, 2, 1], vertical_alignment="center")
    nav_prev.button(
        "", icon=":material/chevron_left:", key="prev", use_container_width=True,
        disabled=sel == 0, on_click=go, args=(sel - 1,), help="Previous bus",
    )
    nav_now.button(
        "Now", icon=":material/my_location:", key="now", use_container_width=True,
        disabled=sel == 0, on_click=go, args=(0,), help="Back to the next bus",
    )
    nav_next.button(
        "", icon=":material/chevron_right:", key="next", use_container_width=True,
        disabled=sel >= len(next_buses) - 1, on_click=go, args=(sel + 1,), help="Next bus",
    )
    html(f"""
<div class="top">
  <span class="chip">{icon("bus", 16)} Bus {bus}</span>
  <span class="chip">{icon("route", 16)} {route}</span>
</div>
<div class="big">{dep_time.strftime("%H:%M")}</div>
<div class="sub">{label} from {origin}</div>
<div class="stats">
  <div class="stat"><div class="lbl">{icon("timer", 14)} Leaves in</div><div class="val">{fmt_minutes(minutes_left)}</div></div>
  <div class="stat"><div class="lbl">{icon("flag", 14)} Arrives</div><div class="val">{arr_txt}</div></div>
  <div class="stat"><div class="lbl">{icon("clock", 14)} Trip</div><div class="val">{duration}</div></div>
</div>
""")

# -----------------------------
# FULL ROUTE TIMELINE + ETA
# -----------------------------
full = df[(df["Route"] == route) & (df["BusNumber"] == bus)].sort_values("StopOrder")

html(f'<div class="section">{icon("list", 20)} Trip timeline</div>')

items = []
for r in full.itertuples():
    t = pd.to_datetime(r.Time)
    eta = int((t - now).total_seconds() / 60)
    cls, tag = [], ""
    if r.Stop == origin:
        cls.append("from")
        tag = '<span class="tag f">FROM</span>'
    elif r.Stop == destination:
        cls.append("to")
        tag = '<span class="tag t">TO</span>'
    if direction_ok:
        if order[origin] <= order[r.Stop] <= order[destination]:
            cls.append("active")
        else:
            cls.append("dim")
    items.append(
        f'<li class="{" ".join(cls)}"><span class="name">{r.Stop} {tag}</span>'
        f'<span class="when"><b>{t.strftime("%H:%M")}</b><small>{fmt_minutes(eta)}</small></span></li>'
    )

html(f'<ul class="tl">{"".join(items)}</ul>')

# -----------------------------
# NEXT BUSES PREVIEW (click to select)
# -----------------------------
html(f'<div class="section">{icon("clock", 20)} Upcoming buses from {origin}</div>')

with st.container(key="nbs"):
    for i in range(min(len(next_buses), max(4, sel + 1))):
        b = next_buses.iloc[i]
        m = int((b["Time"] - now).total_seconds() / 60)
        a = arrival_at_destination(b["BusNumber"]) if direction_ok else None
        arrives = f"  ·  arrives {a.strftime('%H:%M')}" if a is not None else ""
        st.button(
            f"**{b['Time'].strftime('%H:%M')}**  ·  Bus {b['BusNumber']}  ·  {fmt_minutes(m)}{arrives}",
            key=f"nb{i}", icon=":material/directions_bus:", use_container_width=True,
            type="primary" if i == sel else "secondary", on_click=go, args=(i,),
        )
