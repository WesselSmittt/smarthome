import dash
from dash import html, Input, Output
import datetime

# -----------------------------
# App & State
# -----------------------------
app = dash.Dash(__name__)
app.title = "Smart Home Dashboard"

status = {
    "light": True,
    "gas": False,
    "heating": True,
    "water": False
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


def card(name, key, icon):
    on = status[key]
    return html.Div(
        id=f"{key}-card",
        className=f"utility {'on '+key if on else 'off'}",
        children=[
            html.H3(f"{icon} {name}"),
            html.Small("On" if on else "Off"),
            html.Div(className="status", children=[
                html.Span("Status"),
                html.Span("On" if on else "Off")
            ]),
            html.Button(
                "Turn Off" if on else "Turn On",
                id=f"{key}-btn",
                className="btn-off" if on else "btn-on"
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
        html.Div(className="card weather", children=[
            html.Small("☀️ Daytime"),
            html.H1("15°C"),
            html.Small("Amsterdam"),
            html.P("Scattered Clouds"),
            html.Div(className="weather-row", children=[
                html.Div("💧 Humidity 75%"),
                html.Div("🌬️ Wind 3 m/s")
            ])
        ]),

        html.Br(),

        # Utilities (cards rendered immediately)
        html.Div(className="utilities", children=[
            card("Light", "light", "💡"),
            card("Gas", "gas", "💨"),
            card("Heating", "heating", "🔥"),
            card("Water", "water", "🚰"),
        ])
    ]),

    # Right column
    html.Div(className="card recent", children=[
        html.H3("🕒 Recent Changes"),
        html.Div(id="recent-log")
    ])
])


# -----------------------------
# Callbacks
# -----------------------------
@app.callback(
    Output("light-card", "children"),
    Output("gas-card", "children"),
    Output("heating-card", "children"),
    Output("water-card", "children"),
    Output("recent-log", "children"),
    Input("light-btn", "n_clicks"),
    Input("gas-btn", "n_clicks"),
    Input("heating-btn", "n_clicks"),
    Input("water-btn", "n_clicks"),
)
def update(light, gas, heating, water):
    ctx = dash.callback_context
    if ctx.triggered:
        btn = ctx.triggered[0]["prop_id"].split(".")[0]
        if btn == "light-btn": toggle("light", "Light")
        if btn == "gas-btn": toggle("gas", "Gas")
        if btn == "heating-btn": toggle("heating", "Heating")
        if btn == "water-btn": toggle("water", "Water")

    return (
        card("Light", "light", "💡").children,
        card("Gas", "gas", "💨").children,
        card("Heating", "heating", "🔥").children,
        card("Water", "water", "🚰").children,
        recent_changes
    )


if __name__ == "__main__":
    app.run(debug=True)