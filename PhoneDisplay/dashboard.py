import dash
from dash import html, Input, Output, dcc
import datetime, random, requests
import psycopg2
from dotenv import load_dotenv
import os

# -----------------------------
# PostgreSQL Configuration
# -----------------------------
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def db_connect():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print("Database connection failed:", e)
        return None

# -----------------------------
# SENSOR FUNCTIONS (LDR + RFID)
# -----------------------------
def get_light_state_from_ldr():
    try:
        conn = db_connect()
        if conn is None:
            return None

        cur = conn.cursor()
        cur.execute("""
            SELECT light_level
            FROM ldr_readings
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row is None:
            return None

        LDR_THRESHOLD = 500
        return row[0] > LDR_THRESHOLD

    except Exception as e:
        print("LDR read failed:", e)
        return None


def get_door_state_from_rfid():
    try:
        conn = db_connect()
        if conn is None:
            return None

        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp
            FROM rfid_checkin
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row is None:
            return None

        now = datetime.datetime.now(datetime.timezone.utc)
        return (now - row[0]).total_seconds() < 10

    except Exception as e:
        print("RFID read failed:", e)
        return None


def refresh_status_from_sensors(status):
    light = get_light_state_from_ldr()
    door = get_door_state_from_rfid()

    if light is not None:
        status["light"] = light

    if door is not None:
        status["door"] = door

    return status

# -----------------------------
# Weather API
# -----------------------------
def get_weather():
    lat, lon = 52.09, 5.12
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true&hourly=relativehumidity_2m"
    )
    response = requests.get(url)
    data = response.json()

    current = data["current_weather"]
    temp = round(current["temperature"])
    wind = current["windspeed"]
    code = current["weathercode"]

    humidity = data["hourly"]["relativehumidity_2m"][0]

    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
        53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
        63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow fall",
        73: "Moderate snow fall", 75: "Heavy snow fall", 95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    description = weather_codes.get(code, f"Weather code {code}")

    return temp, humidity, wind, description

# -----------------------------
# App & State
# -----------------------------
app = dash.Dash(__name__)
app.title = "Smart Home Dashboard"

status = {
    "light": True,
    "gas": False,
    "heating": True,
    "water": False,
    "door": False
}
recent_changes = []

# -----------------------------
# Helpers
# -----------------------------
def log_change(name, state):
    time = datetime.datetime.now().strftime("%I:%M:%S %p")
    recent_changes.insert(
        0,
        html.Div(
            className="log-item",
            children=[
                html.Div(className="log-title", children=f"{name} turned {'on' if state else 'off'}"),
                html.Div(className="log-time", children=time),
                html.Span("On" if state else "Off", className=f"badge {'on' if state else 'off'}")
            ]
        )
    )
    if len(recent_changes) > 5:
        recent_changes.pop()


def toggle(key, label):
    status[key] = not status[key]
    log_change(label, status[key])


def card(name, key, icon, on):
    auto = key in ("light", "door")

    return html.Div(
        id=f"{key}-card",
        className=f"utility {'on '+key if on else 'off'}",
        children=[
            html.H3(f"{icon} {name}"),
            html.Small("Auto" if auto else ("On" if on else "Off")),
            html.Div(className="status", children=[
                html.Span("Status"),
                html.Span("On" if on else "Off")
            ]),
            html.Button(
                "Auto" if auto else ("Turn Off" if on else "Turn On"),
                id=f"{key}-btn",
                disabled=auto,
                className="btn-disabled" if auto else ("btn-off" if on else "btn-on")
            )
        ]
    )

# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div(className="page", children=[

    # Left column
    html.Div(children=[

        # Weather card
        html.Div(id="weather-card", className="card weather"),
        dcc.Interval(id="weather-interval", interval=60000, n_intervals=0),

        html.Br(),

        # Utilities
        html.Div(className="utilities", children=[
            card("Light", "light", "💡", status["light"]),
            card("Gas", "gas", "💨", status["gas"]),
            card("Heating", "heating", "🔥", status["heating"]),
            card("Water", "water", "🚰", status["water"]),
            card("Door", "door", "🚪", status["door"]),
        ]),

        html.Br(),

        html.Button("Simulate Random Change", id="simulate-btn", className="btn-simulate")
    ]),

    # Right column
    html.Div(children=[

        html.Div(className="card recent", children=[
            html.H3("🕒 Recent Changes"),
            html.Div(id="recent-log")
        ])
    ])
])

# -----------------------------
# Weather Callback
# -----------------------------
@app.callback(
    Output("weather-card", "children"),
    Input("weather-interval", "n_intervals")
)
def update_weather(_):
    try:
        temp, humidity, wind, description = get_weather()
        return [
            html.Small("☀️ Utrecht"),
            html.H1(f"{temp}°C"),
            html.P(description),
            html.Div(className="weather-row", children=[
                html.Div(f"💧 Humidity {humidity}%"),
                html.Div(f"🌬️ Wind {wind} m/s")
            ])
        ]
    except Exception as e:
        return [html.Small("Weather unavailable"), html.P(str(e))]

# -----------------------------
# Utility Callback
# -----------------------------
@app.callback(
    Output("light-card", "children"),
    Output("gas-card", "children"),
    Output("heating-card", "children"),
    Output("water-card", "children"),
    Output("door-card", "children"),
    Output("recent-log", "children"),
    Input("light-btn", "n_clicks"),
    Input("gas-btn", "n_clicks"),
    Input("heating-btn", "n_clicks"),
    Input("water-btn", "n_clicks"),
    Input("door-btn", "n_clicks"),
    Input("simulate-btn", "n_clicks"),
)
def update(*args):
    global status

    # AUTO SENSOR UPDATE
    status = refresh_status_from_sensors(status)

    ctx = dash.callback_context
    if ctx.triggered:
        btn = ctx.triggered[0]["prop_id"].split(".")[0]

        # Manual toggles (only for non-sensor devices)
        if btn == "gas-btn": toggle("gas", "Gas")
        if btn == "heating-btn": toggle("heating", "Heating")
        if btn == "water-btn": toggle("water", "Water")

        # SIMULATION — ONLY gas/heating/water
        if btn == "simulate-btn":
            sim_keys = ["gas", "heating", "water"]
            num_to_toggle = random.randint(0, len(sim_keys))
            choices = random.sample(sim_keys, num_to_toggle)

            for choice in choices:
                status[choice] = not status[choice]

            time = datetime.datetime.now().strftime("%I:%M:%S %p")
            if choices:
                recent_changes.insert(
                    0,
                    html.Div(
                        className="log-item",
                        children=[
                            html.Div(className="log-title",
                                     children=f"Simulation toggled: {', '.join(c.capitalize() for c in choices)}"),
                            html.Span("Mixed", className="badge simulate")
                        ]
                    )
                )
            else:
                recent_changes.insert(
                    0,
                    html.Div(
                        className="log-item",
                        children=[
                            html.Div(className="log-title", children="Simulation made no changes"),
                            html.Div(className="log-time", children=time),
                            html.Span("None", className="badge simulate")
                        ]
                    )
                )

            if len(recent_changes) > 5:
                recent_changes.pop()

    return (
        card("Light", "light", "💡", status["light"]).children,
        card("Gas", "gas", "💨", status["gas"]).children,
        card("Heating", "heating", "🔥", status["heating"]).children,
        card("Water", "water", "🚰", status["water"]).children,
        card("Door", "door", "🚪", status["door"]).children,
        recent_changes
    )

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)


