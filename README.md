# UOsaka Shuttle

<p align="center">
  <img src="logo.svg" alt="UOsaka Shuttle logo" width="160">
</p>

<p align="center">
  <a href="https://shuttle.streamlit.app/">
    <img src="https://img.shields.io/badge/Open%20the%20app-2563eb?style=for-the-badge&logo=streamlit&logoColor=white" alt="Open the live app">
  </a>
</p>

A simple Streamlit webapp showing the Osaka University shuttle bus timetable between campuses.

> **Unofficial app.** This project is for personal use and not affiliated with Osaka University. Times and stops may not be accurate.
> For official information see the [Osaka University bus page](https://www.osaka-u.ac.jp/en/access/bus).

## Features

- Pick a route and From/To stops.
- See the next bus, with departure time, countdown, arrival time and trip duration.
- Step through earlier/later buses, or jump back to the next one with **Now**.
- Full trip timeline with the time at every stop.
- Map with the buses currently on the road.
Positions are **estimated from the timetable** and are not real-time.
Click on a bus for timetable information.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Data

- `buses.csv`: timetable (route, stop, bus number, time, stop order).
- `stops.csv`: approximate stop coordinates used by the map.

Road paths on the map are fetched from [OSRM](https://project-osrm.org/) and map tiles come from [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
