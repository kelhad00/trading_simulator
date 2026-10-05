"""Moving-candles prototype (TradingView-style forming candles).

Standalone: loads the same session.zip that TradeSim exports, but never writes to
Data/ and doesn't import or change anything in trade/. Runs on port 8052, so
TradeSim (8050) can run at the same time.

    python prototypes/moving_candles/app.py [--zip "path/to/session.zip"] [--port 8052]

Then open http://127.0.0.1:8052
"""
import argparse
import base64
import zlib

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update

from load_session import load_session
from sub_steps import split_candle

# One user, one session at a time: kept in memory, never written to disk
SESSION = {"data": None, "name": None}

STEP_CHOICES = [2, 3, 4, 6, 12]
SPEED_CHOICES = {"Slow (2 s)": 2000, "Normal (1 s)": 1000, "Fast (0.5 s)": 500, "Very fast (0.2 s)": 200}

LABEL = {"fontWeight": 600, "fontSize": 13, "marginBottom": 4}
BOX = {"display": "flex", "flexDirection": "column", "minWidth": 150}


def seed_for(ticker, i):
    """Same candle always plays the same way."""
    return zlib.crc32(f"{ticker}|{i}".encode())


def company_options():
    s = SESSION["data"]
    if s is None:
        return []
    return [{"label": f"{label} ({n} candles)", "value": t}
            for t, label in s.companies.items()
            for n in [len(s.candles(t))]]


app = Dash(__name__, title="Moving candles prototype")

app.layout = html.Div(style={"fontFamily": "Arial, sans-serif", "maxWidth": 1200, "margin": "0 auto", "padding": 16}, children=[
    html.H2("Moving candles prototype", style={"marginBottom": 0}),
    html.Div("Each candle forms step by step (like a 1 h candle updated at 15, 30, 45 min, then closed). "
             "Reads session.zip in memory: nothing is written to Data/.",
             style={"color": "#666", "marginBottom": 12}),

    dcc.Upload(id="upload", accept=".zip", children=html.Div(id="upload-text", children="Drop session.zip here or click to choose it"),
               style={"border": "2px dashed #aaa", "borderRadius": 8, "padding": 14, "textAlign": "center",
                      "cursor": "pointer", "marginBottom": 12}),

    html.Div(style={"display": "flex", "gap": 16, "flexWrap": "wrap", "alignItems": "flex-end", "marginBottom": 12}, children=[
        html.Div(style={**BOX, "minWidth": 320}, children=[
            html.Span("Company", style=LABEL),
            dcc.Dropdown(id="company", options=company_options(), clearable=False),
        ]),
        html.Div(style=BOX, children=[
            html.Span("Steps per candle", style=LABEL),
            dcc.Dropdown(id="n-steps", options=STEP_CHOICES, value=4, clearable=False),
        ]),
        html.Div(style=BOX, children=[
            html.Span("Speed (time per step)", style=LABEL),
            dcc.Dropdown(id="speed", options=[{"label": k, "value": v} for k, v in SPEED_CHOICES.items()],
                         value=1000, clearable=False),
        ]),
        html.Div(style=BOX, children=[
            html.Span("Candles already shown at start", style=LABEL),
            dcc.Input(id="start-at", type="number", min=1, value=30, style={"height": 32}),
        ]),
        html.Button("▶ Play", id="play", n_clicks=0, style={"height": 36, "minWidth": 90}),
        html.Button("Next step", id="next", n_clicks=0, style={"height": 36}),
        html.Button("Reset", id="reset", n_clicks=0, style={"height": 36}),
    ]),

    html.Div(id="info", style={"background": "#f3f5f8", "borderRadius": 8, "padding": "10px 14px",
                               "fontSize": 14, "lineHeight": 1.6, "marginBottom": 8}),
    dcc.Graph(id="chart", style={"height": "62vh"}, config={"displaylogo": False}),

    dcc.Interval(id="tick", interval=1000, disabled=True),
    # Position: candles [0, candle) are closed, candle `candle` is at `step` (0 = not started)
    dcc.Store(id="pos", data={"candle": 30, "step": 0}),
])


@app.callback(
    Output("upload-text", "children"),
    Output("company", "options"),
    Output("company", "value"),
    Input("upload", "contents"),
    State("upload", "filename"),
)
def on_upload(contents, filename):
    if contents is None:  # first load: use --zip if one was given
        opts = company_options()
        text = (f"Loaded: {SESSION['name']} (drop another session.zip to replace it)" if SESSION["data"]
                else "Drop session.zip here or click to choose it")
        return text, opts, (opts[0]["value"] if opts else None)
    try:
        raw = base64.b64decode(contents.split(",", 1)[1])
        SESSION["data"] = load_session(raw)
        SESSION["name"] = filename
    except Exception as e:  # show the problem instead of crashing
        return f"Could not read {filename}: {e}", no_update, no_update
    opts = company_options()
    return f"Loaded: {filename} (drop another session.zip to replace it)", opts, (opts[0]["value"] if opts else None)


@app.callback(
    Output("tick", "disabled"),
    Output("play", "children"),
    Input("play", "n_clicks"),
    State("tick", "disabled"),
    prevent_initial_call=True,
)
def toggle_play(_, disabled):
    return (False, "⏸ Pause") if disabled else (True, "▶ Play")


@app.callback(Output("tick", "interval"), Input("speed", "value"))
def set_speed(ms):
    return ms


@app.callback(
    Output("pos", "data"),
    Input("tick", "n_intervals"),
    Input("next", "n_clicks"),
    Input("reset", "n_clicks"),
    Input("company", "value"),
    Input("n-steps", "value"),
    Input("start-at", "value"),
    State("pos", "data"),
)
def move(_tick, _next, _reset, company, n_steps, start_at, pos):
    s = SESSION["data"]
    if s is None or company is None:
        return no_update
    total = len(s.candles(company))
    start = min(max(int(start_at or 1), 1), total - 1)

    if ctx.triggered_id not in ("tick", "next"):
        return {"candle": start, "step": 0}  # reset / new settings: start over

    candle, step = pos["candle"], pos["step"]
    if candle >= total:
        return no_update  # end of data
    if step < n_steps:
        return {"candle": candle, "step": step + 1}
    return {"candle": candle + 1, "step": 1 if candle + 1 < total else 0}


def fmt(v):
    return f"€{v:,.2f}"


@app.callback(
    Output("chart", "figure"),
    Output("info", "children"),
    Input("pos", "data"),
    State("company", "value"),
    State("n-steps", "value"),
)
def draw(pos, company, n_steps):
    s = SESSION["data"]
    if s is None or company is None:
        return go.Figure(), "Load a session.zip to start."

    df = s.candles(company)
    total = len(df)
    candle, step = min(pos["candle"], total), pos["step"]

    closed = df.iloc[:candle]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=closed.index, open=closed.Open, high=closed.High, low=closed.Low, close=closed.Close,
        name="Closed candles",
    ))

    shown_high = closed.High.max() if len(closed) else None
    shown_low = closed.Low.min() if len(closed) else None

    if step > 0 and candle < total:
        real = df.iloc[candle]
        o, h, l, c = split_candle(real.Open, real.High, real.Low, real.Close, n_steps,
                                  seed_for(company, candle))[step - 1]
        is_closing = step == n_steps
        fig.add_trace(go.Candlestick(
            x=[df.index[candle]], open=[o], high=[h], low=[l], close=[c],
            name="Forming candle",
            increasing=dict(line=dict(color="#1565c0"), fillcolor="#64b5f6"),
            decreasing=dict(line=dict(color="#e65100"), fillcolor="#ffb74d"),
        ))
        fig.add_hline(y=c, line_dash="dash", line_width=1, line_color="gray",
                      annotation_text=fmt(c), annotation_position="top right",
                      annotation_bgcolor="gray", annotation_font_color="white")
        shown_high = h if shown_high is None else max(shown_high, h)
        shown_low = l if shown_low is None else min(shown_low, l)

        minutes = round(60 * step / n_steps)
        matches = (o, h, l, c) == (real.Open, real.High, real.Low, real.Close)
        info = [
            html.B(f"Candle {candle + 1} of {total}  ·  {df.index[candle]:%a %d %b %Y}  ·  "
                   f"step {step} of {n_steps}"),
            html.Span(f"  (like minute {minutes} of a 1-hour candle{', CLOSED' if is_closing else ''})"),
            html.Br(),
            f"Forming candle now:  open {fmt(o)}  ·  high {fmt(h)}  ·  low {fmt(l)}  ·  close/price {fmt(c)}",
            html.Br(),
            html.Span(
                (f"Real candle in the file:  open {fmt(real.Open)}  ·  high {fmt(real.High)}  ·  "
                 f"low {fmt(real.Low)}  ·  close {fmt(real.Close)}  →  "
                 + ("✔ closed candle matches the file exactly" if matches else "✘ does NOT match"))
                if is_closing else "Real candle in the file: hidden until the candle closes (traders can't see the future).",
                style={"color": "#2e7d32" if is_closing and matches else "#666"},
            ),
        ]
    elif candle >= total:
        info = html.B(f"End of data: all {total} candles closed.")
    else:
        info = [html.B(f"{candle} candles shown. "), "Press ▶ Play or Next step to start forming the next candle."]

    # Fixed x range over the whole file (fills left to right, like TradeSim's chart);
    # price axis padded 15% around what has been shown so far
    day = df.index[1] - df.index[0] if total > 1 else None
    x_range = [df.index[0] - day, df.index[-1] + day] if day is not None else None
    pad = (shown_high - shown_low) * 0.15 or shown_high * 0.01
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(range=x_range, rangeslider=dict(visible=False)),
        yaxis=dict(range=[shown_low - pad, shown_high + pad], side="right", tickprefix="€", tickformat=",.2f"),
        legend=dict(orientation="h", x=0, y=1.0, xanchor="left", yanchor="bottom"),
        uirevision=company,  # keep the user's zoom while playing
    )
    return fig, info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moving-candles prototype")
    parser.add_argument("--zip", help="session.zip to load at start (you can also drop one in the page)")
    parser.add_argument("--port", type=int, default=8052)
    args = parser.parse_args()

    if args.zip:
        SESSION["data"] = load_session(args.zip)
        SESSION["name"] = args.zip
        print(f"Loaded {args.zip}: {len(SESSION['data'].companies)} companies")

    print(f"Open http://127.0.0.1:{args.port}")
    app.run_server(debug=False, port=args.port)
