import streamlit as st
import json
import pandas as pd
import requests
import streamlit.components.v1 as components

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Shuttle Bus", page_icon="favicon.png", layout="centered")

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
  border-radius: 16px !important; padding: 1.25rem !important; margin: 1rem 0; gap: 1rem; }
.st-key-hero [data-testid="stMarkdownContainer"] p { margin: 0; }
.st-key-hero .stats { margin-top: .5rem; }
.fine { color: var(--muted); font-size: .75rem; line-height: 1.4; }
.fine a { color: inherit; text-decoration: underline; }
.footer { margin-top: 2rem; text-align: center; }
.st-key-hero .stats .stat { padding-bottom: 0; }
.st-key-hero [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .5rem; }
.st-key-hero [data-testid="stColumn"] { min-width: 0 !important; }
.st-key-hero button { border-radius: 10px; }
.st-key-hero iframe { border-radius: 12px; border: 1px solid var(--border); }
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
  <div><h1>Shuttle Bus</h1><p>Live timetable &middot; Asia/Osaka</p></div>
</div>
""")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("buses.csv")
raw_df = df[["Route", "Stop", "BusNumber", "StopOrder"]].assign(
    Minutes=pd.to_datetime(df["Time"], format="%H:%M").dt.hour * 60
    + pd.to_datetime(df["Time"], format="%H:%M").dt.minute
)
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
# MAP DATA (stations, road paths, ideal schedule)
# -----------------------------
stop_coords = pd.read_csv("stops.csv").set_index("Stop")[["Lat", "Lon"]]


@st.cache_data(show_spinner=False)
def road_path(a, b):
    """Driving path a -> b as [[lat, lon], ...] via OSRM, straight line on failure."""
    (la, lo), (lb, lob) = a, b
    try:
        url = (
            f"https://router.project-osrm.org/route/v1/driving/{lo},{la};{lob},{lb}"
            "?overview=full&geometries=geojson"
        )
        coords = requests.get(url, timeout=6).json()["routes"][0]["geometry"]["coordinates"]
        return [[lat, lon] for lon, lat in coords]
    except Exception:
        return [[la, lo], [lb, lob]]


def map_payload(route, origin, destination, theme):
    names = route_stops(route)
    path, stop_list = [], []
    for i, n in enumerate(names):
        c = (float(stop_coords.loc[n, "Lat"]), float(stop_coords.loc[n, "Lon"]))
        if i == 0:
            path.append(list(c))
        else:
            prev = stop_list[-1]
            seg = road_path((prev["lat"], prev["lon"]), c)
            path.extend(seg[1:])
        stop_list.append({"name": n, "lat": c[0], "lon": c[1], "idx": len(path) - 1})
    idx = {s["name"]: i for i, s in enumerate(stop_list)}
    trips, shortcuts = [], {}
    r = raw_df[raw_df["Route"] == route]
    for bus_no, g in r.groupby("BusNumber"):
        g = g.sort_values("StopOrder")
        # A trip that skips stops drives directly between the ones it serves
        served = [idx[s] for s in g["Stop"]]
        for i0, i1 in zip(served, served[1:]):
            if i1 - i0 > 1 and f"{i0}-{i1}" not in shortcuts:
                a, b = stop_list[i0], stop_list[i1]
                shortcuts[f"{i0}-{i1}"] = road_path((a["lat"], a["lon"]), (b["lat"], b["lon"]))
        trips.append({
            "bus": int(bus_no),
            "stops": [[idx[s], int(m)] for s, m in zip(g["Stop"], g["Minutes"])],
        })
    return {
        "path": path, "stops": stop_list, "trips": trips, "shortcuts": shortcuts,
        "origin": idx[origin], "destination": idx[destination], "theme": theme,
    }


MAP_HTML = """
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body, #map { height: 100%; margin: 0; font-family: system-ui, sans-serif; }
  .bus { width: 34px; height: 34px; border-radius: 50%; background: #2563eb; color: #fff;
    border: 3px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,.4); display: flex;
    align-items: center; justify-content: center; }
  .stn { width: 14px; height: 14px; border-radius: 50%; background: #fff;
    border: 4px solid #1e293b; box-sizing: border-box; box-shadow: 0 1px 4px rgba(0,0,0,.4); }
  .stn.from { border-color: #16a34a; } .stn.to { border-color: #dc2626; }
  .lbl { background: rgba(255,255,255,.92); border: 0; box-shadow: 0 1px 3px rgba(0,0,0,.3);
    font-weight: 600; font-size: 11px; padding: 1px 6px; }
  .tick b { font-size: 14px; } .tick div { margin-top: 2px; font-size: 13px; }
  body.dark .leaflet-tile-pane { filter: invert(1) hue-rotate(180deg) brightness(.95) contrast(.9); }
  body.dark .lbl, body.dark #empty { background: rgba(30,41,59,.92); color: #e2e8f0; }
  body.dark .leaflet-tooltip-top.lbl::before { border-top-color: rgba(30,41,59,.92); }
  body.dark .leaflet-popup-content-wrapper, body.dark .leaflet-popup-tip { background: #1e293b; color: #e2e8f0; }
  body.dark .stn { background: #1e293b; }
  body.dark .leaflet-control-zoom a { background: #1e293b; color: #e2e8f0; border-color: #475569; }
  body.dark .leaflet-control-attribution { background: rgba(30,41,59,.8); color: #94a3b8; }
  body.dark .leaflet-control-attribution a { color: #cbd5e1; }
  #empty { position: absolute; z-index: 1000; left: 50%; bottom: 12px; transform: translateX(-50%);
    background: rgba(255,255,255,.95); padding: 4px 12px; border-radius: 999px; font-size: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,.3); display: none; }
</style>
<div id="map"></div><div id="empty">No buses on the road right now</div>
<script>
const D = __DATA__;
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const hhmm = m => String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
const BUS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6v6"/><path d="M15 6v6"/><path d="M2 12h19.6"/><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/><circle cx="7" cy="18" r="2"/><path d="M9 18h5"/><circle cx="16" cy="18" r="2"/></svg>';

document.body.classList.toggle('dark', D.theme === 'dark');
const map = L.map('map', {scrollWheelZoom: false, closePopupOnClick: true});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'}).addTo(map);
L.polyline(D.path, {color: '#2563eb', weight: 5, opacity: .55}).addTo(map);
map.fitBounds(L.polyline(D.path).getBounds(), {padding: [40, 40]});

D.stops.forEach((s, i) => {
  const cls = i === D.origin ? 'from' : i === D.destination ? 'to' : '';
  L.marker([s.lat, s.lon], {
    icon: L.divIcon({className: '', html: '<div class="stn ' + cls + '"></div>', iconSize: [14, 14]}),
    zIndexOffset: 500,
  }).addTo(map).bindTooltip(esc(s.name), {permanent: true, direction: 'top', offset: [0, -8], className: 'lbl'});
});

// cumulative distance along a path
const cumOf = p => { const c = [0]; for (let i = 1; i < p.length; i++) c.push(c[i - 1] + map.distance(p[i - 1], p[i])); return c; };
function at(p, c, d) {
  let i = 1;
  while (i < c.length - 1 && c[i] < d) i++;
  const f = c[i] === c[i - 1] ? 0 : (d - c[i - 1]) / (c[i] - c[i - 1]);
  const a = p[i - 1], b = p[i];
  return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
}
const cum = cumOf(D.path);
const stopDist = i => cum[D.stops[i].idx];
// drive straight between stops a trip serves when it skips the ones in between
const short = {};
Object.entries(D.shortcuts).forEach(([k, p]) => {
  short[k] = {p, c: cumOf(p)};
  L.polyline(p, {color: '#2563eb', weight: 3, opacity: .5, dashArray: '6 8'}).addTo(map);
});
function between(i0, i1, f) {
  const sc = short[i0 + '-' + i1];
  if (sc) return at(sc.p, sc.c, sc.c[sc.c.length - 1] * f);
  return at(D.path, cum, stopDist(i0) + (stopDist(i1) - stopDist(i0)) * f);
}

// ideal position of a trip at time t (minutes), or null when not traveling
function position(trip, t) {
  const s = trip.stops;
  if (s.length < 2 || t < s[0][1] || t > s[s.length - 1][1]) return null;
  for (let k = 1; k < s.length; k++) {
    if (t <= s[k][1]) {
      const [i0, t0] = s[k - 1], [i1, t1] = s[k];
      const f = t1 === t0 ? 1 : (t - t0) / (t1 - t0);
      return between(i0, i1, f);
    }
  }
  return null;
}
const timeAt = (trip, stop) => { const h = trip.stops.find(x => x[0] === stop); return h ? hhmm(h[1]) : '–'; };

function tokyoMinutes() {
  const p = new Intl.DateTimeFormat('en-GB', {timeZone: 'Asia/Tokyo', hour: '2-digit', minute: '2-digit',
    second: '2-digit', hour12: false}).formatToParts(new Date());
  const g = k => +p.find(x => x.type === k).value;
  return (g('hour') % 24) * 60 + g('minute') + g('second') / 60;
}

const markers = {};
function tick() {
  const t = tokyoMinutes();
  let n = 0;
  D.trips.forEach(trip => {
    const pos = position(trip, t);
    const m = markers[trip.bus];
    if (!pos) { if (m) { m.remove(); delete markers[trip.bus]; } return; }
    n++;
    if (m) { m.setLatLng(pos); return; }
    const mk = L.marker(pos, {
      icon: L.divIcon({className: '', html: '<div class="bus">' + BUS + '</div>', iconSize: [34, 34]}),
      zIndexOffset: 1000,
    }).addTo(map);
    mk.bindPopup('<div class="tick"><b>Bus ' + esc(trip.bus) + '</b>' +
      '<div>Departs ' + esc(D.stops[D.origin].name) + ': <b>' + timeAt(trip, D.origin) + '</b></div>' +
      '<div>Arrives ' + esc(D.stops[D.destination].name) + ': <b>' + timeAt(trip, D.destination) + '</b></div></div>');
    markers[trip.bus] = mk;
  });
  document.getElementById('empty').style.display = n ? 'none' : 'block';
}
tick();
setInterval(tick, 1000);
</script>
"""

def footer():
    html(
        '<div class="fine footer">Unofficial app. Times may not be accurate. '
        'For official information see the '
        '<a href="https://www.osaka-u.ac.jp/en/access/bus" target="_blank" rel="noopener">'
        'official bus page</a>.</div>'
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
    footer()
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
""")
    try:
        theme = "dark" if st.context.theme.type == "dark" else "light"
    except Exception:
        theme = "light"
    map_html = MAP_HTML.replace(
        "__DATA__", json.dumps(map_payload(route, origin, destination, theme)).replace("</", "<\\/")
    )
    if hasattr(st, "iframe"):
        st.iframe(map_html, height=360)
    else:
        components.html(map_html, height=360)
    html('<div class="fine">Not a real-time map: bus positions are estimated from the timetable.</div>')
    html(f"""
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

footer()
