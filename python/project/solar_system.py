#### RENAME THIS FILE
# Rename `project.py` to `(your_project_short_name).py`
# Example: `orbit_simulation.py`, `wave_packet.py`, `two_body_problem.py`

# -----------------------------------------------------------------------------
# PROJECT FILE STRUCTURE (CONTEMPORARY PYTHON BEST PRACTICES)
# -----------------------------------------------------------------------------
# The goal is clarity, testability, and “import safety” (importing your module
# should NOT start the simulation or pop up plots).
#
# Recommended top-to-bottom order:
# 1) Module docstring (100–200 words): what the project does, key assumptions,
#    inputs/outputs, and how to run it.
# 2) Imports (grouped per PEP 8).
# 3) Module-level constants (only if truly global and stable).
# 4) Function definitions (each with a PEP 257-compliant docstring).
# 5) main() function: the single clear entry point for running the program.
# 6) Script guard: if __name__ == "__main__": main()
#
# References:
# - PEP 8 (imports and general style): https://peps.python.org/pep-0008/  (see “Imports”)
# - SciPy physical constants (use inside functions when appropriate):
#   https://docs.scipy.org/doc/scipy/reference/constants.html
#
# -----------------------------------------------------------------------------
# IMPORTS: ORDER + PRACTICES (PEP 8)
# -----------------------------------------------------------------------------
# Put imports at the top, after the module docstring, before constants.
# Group imports in THIS order, separated by blank lines:
#   1) Standard library imports (e.g., math, pathlib, dataclasses)
#   2) Third-party imports (e.g., numpy, scipy, matplotlib, plotly)
#   3) Local/project imports (your own modules in this repo/package)
#
# Examples:
#   # 1) Standard library
#   from __future__ import annotations
#   from dataclasses import dataclass
#   from pathlib import Path
#
#   # 2) Third-party
#   import numpy as np
#   from scipy import constants as scipy_constants
#
#   # 3) Local imports (if your project is a package)
#   # from .helpers import integrate
#
# Avoid:
# - wildcard imports: `from module import *`
# - hiding heavy work at import time (reading big files / launching plots)
#
# -----------------------------------------------------------------------------
# SIMULATION / VISUALIZATION FUNCTIONS (FUNCTIONAL STYLE)
# -----------------------------------------------------------------------------
# Keep “work” inside functions. This makes your code testable and reusable.
#
# Typical breakdown:
# - read_data(...): load/validate input data
# - compute_derived_parameters(...): compute values that depend on inputs
# - simulate(...): compute arrays / time series (no plotting)
# - build_figure(...): create a plot/animation object (no file I/O)
# - save_outputs(...): optional, write files if required
#
# Each function must have:
# - clear, full-word parameter names (PEP 8: lower_case_with_underscores)
# - units in comments or docstrings (meters, seconds, kg, etc.)
# - a docstring describing: parameters, returns, and assumptions
#
# -----------------------------------------------------------------------------
# SciPy CONSTANTS: WHERE TO USE THEM
# -----------------------------------------------------------------------------
# Prefer importing SciPy constants inside the function that uses them, so the
# dependency is obvious and to keep module import fast/lightweight.
#
# Example pattern (inside a function):
#   from scipy import constants as scipy_constants
#   speed_of_light = scipy_constants.c
#
# Docs: https://docs.scipy.org/doc/scipy/reference/constants.html
#
# -----------------------------------------------------------------------------
# main(): THE STANDARD ENTRY POINT
# -----------------------------------------------------------------------------
# It is now standard practice to put the “run the program” logic in a main()
# function and call it under the script guard. This prevents side effects when
# importing your module.
#
# Skeleton:
#   def main() -> None:
#       """Run the simulation and display/save results."""
#       # 1) Define simulation parameters (with units)
#       # 2) Compute derived parameters
#       # 3) Call read_data / simulate / build_figure
#       # 4) Show or save outputs
#
#   if __name__ == "__main__":
#       main()
#
# -----------------------------------------------------------------------------
# PRIMARY SIMULATION FUNCTION STRUCTURE (SUGGESTED)
# -----------------------------------------------------------------------------
# Inside your primary simulation function (often called by main()):
# 1) Parameters (named clearly, units documented)
# 2) Derived parameters (computed from inputs)
# 3) Call helpers for:
#    - data read-in / validation
#    - simulation computation
#    - visualization creation
# 4) Return results (arrays, figure objects) instead of printing everything
#
# Keep plotting separate from physics/math wherever practical.

"""
solar_system.py

Single-file implementation of the Solar System interactive app.

What this module does
- Loads authoritative JSON files from project/data/planets.
- Loads user-authored Markdown pages from project/data/facts.
- Provides a simple cached fetcher stub for authoritative APIs (writes to project/data/cache).
- Builds Plotly figures for three screens: inner, outer, trans-Neptunian.
- Creates a Dash app with navigation, clickable markers, and detail pages.
- Keeps heavy imports inside functions to avoid side effects at import time.

Run
- From repository root:
    python -m project.solar_system
"""
# 1) Standard library
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import json
import time

# 2) Third-party
# Keep heavy UI imports inside functions to avoid import-time side effects.

# 3) Local constants (lightweight)
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
PLANETS_DIR = DATA_DIR / "planets"
FACTS_DIR = DATA_DIR / "facts"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# Data loading and schema
# -------------------------
def read_body_json(body_id: str) -> Dict[str, Any]:
    """
    Load authoritative JSON for a body.

    Parameters
    ----------
    body_id : str
        Unique id/slug for the body (e.g., "mars").

    Returns
    -------
    dict
        Parsed JSON dictionary.

    Raises
    ------
    FileNotFoundError
        If the JSON file does not exist.
    """
    path = PLANETS_DIR / f"{body_id}.json"
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def load_all_bodies() -> Dict[str, Dict[str, Any]]:
    """
    Load all JSON files from project/data/planets.

    Returns
    -------
    dict
        Mapping body_id -> metadata dict.
    """
    bodies: Dict[str, Dict[str, Any]] = {}
    for p in PLANETS_DIR.glob("*.json"):
        with open(p, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            bodies[data["id"]] = data
    return bodies

def load_body_with_facts(body_id: str) -> Dict[str, Any]:
    """
    Load a single body's JSON and its Markdown facts (converted to HTML).

    Parameters
    ----------
    body_id : str

    Returns
    -------
    dict
        {'meta': <json dict>, 'facts_html': <str>}
    """
    meta = read_body_json(body_id)
    facts_path = FACTS_DIR / f"{body_id}.md"
    facts_html = ""
    if facts_path.exists():
        # import markdown locally to avoid heavy import at module load
        import markdown
        with open(facts_path, "r", encoding="utf-8") as fh:
            md = fh.read()
            facts_html = markdown.markdown(md)
    return {"meta": meta, "facts_html": facts_html}

# -------------------------
# Simple cached fetcher stub
# -------------------------
def fetch_and_cache(endpoint_name: str, fetcher_callable) -> dict:
    """
    Generic fetch-and-cache helper.

    Parameters
    ----------
    endpoint_name : str
        Name used for cache filename.
    fetcher_callable : callable
        Function that performs the network call and returns a dict.

    Returns
    -------
    dict
        Response JSON (from cache if available or fetcher_callable result).
    """
    cache_file = CACHE_DIR / f"{endpoint_name}.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    # attempt fetch with simple backoff
    backoff = 1.0
    for attempt in range(3):
        try:
            data = fetcher_callable()
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            return data
        except Exception:
            time.sleep(backoff)
            backoff *= 2
    # final fallback: empty dict
    return {}

# Example fetcher callable you can replace with real NASA calls
def example_nasa_fetcher_stub() -> dict:
    """
    Placeholder fetcher that simulates an API response.
    Replace with real requests.get calls as needed.
    """
    return {"note": "This is a stub. Replace with real API call and API key."}

# -------------------------
# Utility computations
# -------------------------
def compute_circumference_from_radius(radius_km: float) -> float:
    """
    Compute circumference (km) from radius (km).

    Parameters
    ----------
    radius_km : float

    Returns
    -------
    float
        Circumference in kilometers.
    """
    from math import tau
    return tau * radius_km

# -------------------------
# Plotly figure builder
# -------------------------
def build_diagram_figure(screen: str, bodies: Dict[str, Dict[str, Any]]):
    """
    Build a Plotly figure for a given screen.

    Parameters
    ----------
    screen : str
        One of 'inner', 'outer', 'trans'
    bodies : dict
        Mapping body_id -> body metadata

    Returns
    -------
    plotly.graph_objects.Figure
    """
    # import Plotly locally
    import plotly.graph_objects as go

    xs, ys, texts, ids, sizes = [], [], [], [], []
    # mapping of screens to ids (explicit to match your list)
    inner_ids = {"sun", "mercury", "venus", "earth", "mars", "asteroid_belt"}
    outer_ids = {"jupiter", "saturn", "uranus", "neptune", "kuiper_belt"}
    trans_ids = {"pluto", "eris", "voyager_1", "voyager_2", "kuiper_belt"}

    for bid, meta in bodies.items():
        if screen == "inner" and bid in inner_ids:
            r = meta.get("distance_au", 0.1)
        elif screen == "outer" and bid in outer_ids:
            r = meta.get("distance_au", 5.0)
        elif screen == "trans" and bid in trans_ids:
            r = meta.get("distance_au", 30.0)
        else:
            continue
        # simple layout: place along x axis with small jitter
        xs.append(r)
        ys.append(0)
        texts.append(meta.get("name", bid))
        ids.append(bid)
        sizes.append(max(8, min(40, (meta.get("circumference_km") or 1000) / 1000)))
    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(size=sizes, color="lightblue"),
        text=texts,
        customdata=ids
    ))
    fig.update_layout(title=f"{screen.title()} Solar System", xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# -------------------------
# Dash app creation
# -------------------------
def create_dash_app() -> "Dash":
    """
    Create and configure the Dash app instance.

    Returns
    -------
    Dash
    """
    # local imports for UI
    from dash import Dash, html, dcc, Input, Output, State
    import dash_bootstrap_components as dbc

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    bodies = load_all_bodies()
    # default figure for inner screen
    fig = build_diagram_figure("inner", bodies)

    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.Button("Inner", id="btn-inner", color="primary", className="me-1"),
                dbc.Button("Outer", id="btn-outer", color="secondary", className="me-1"),
                dbc.Button("Trans", id="btn-trans", color="info", className="me-1"),
            ],
            brand="Solar System Explorer",
            color="dark",
            dark=True,
        ),
        html.Div(id="main-content", children=[
            dcc.Graph(id="diagram-graph", figure=fig, config={"displayModeBar": False}),
            html.Div(id="detail-container")
        ]),
        dcc.Store(id="bodies-store", data=bodies)
    ])

    # navigation callbacks
    @app.callback(
        Output("diagram-graph", "figure"),
        Input("btn-inner", "n_clicks"),
        Input("btn-outer", "n_clicks"),
        Input("btn-trans", "n_clicks"),
        State("bodies-store", "data"),
        prevent_initial_call=True
    )
    def switch_screen(n1, n2, n3, bodies_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            return build_diagram_figure("inner", bodies_data)
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if btn_id == "btn-inner":
            return build_diagram_figure("inner", bodies_data)
        if btn_id == "btn-outer":
            return build_diagram_figure("outer", bodies_data)
        return build_diagram_figure("trans", bodies_data)

    # click -> show detail
    @app.callback(
        Output("detail-container", "children"),
        Input("diagram-graph", "clickData"),
        State("bodies-store", "data")
    )
    def show_detail(clickData, bodies_data):
        if not clickData:
            return ""
        body_id = clickData["points"][0]["customdata"]
        combined = load_body_with_facts(body_id)
        meta = combined["meta"]
        facts_html = combined["facts_html"] or "<p>No extended facts available.</p>"
        # build a simple detail layout
        table_rows = []
        # fields to show for planets/dwarf planets
        keys = [
            ("Distance from sun (AU)", meta.get("distance_au")),
            ("Type", meta.get("planet_type") or meta.get("type")),
            ("Composition", meta.get("composition")),
            ("Circumference (km)", meta.get("circumference_km")),
            ("Mass (kg)", meta.get("mass_kg")),
            ("Atmosphere", meta.get("atmosphere")),
            ("Orbit type / Period (days)", f"{meta.get('orbit_type')} / {meta.get('orbital_period_days')}"),
            ("Rotation period (hours)", meta.get("rotation_period_hours")),
            ("Moons (count / notable)", f"{meta.get('moon_count')} / {meta.get('notable_moons')}"),
            ("Rings", meta.get("rings")),
        ]
        for label, val in keys:
            table_rows.append(html.Tr([html.Th(label), html.Td(str(val) if val is not None else "—")]))

        detail = html.Div([
            html.H3(meta.get("name", body_id)),
            html.Table(table_rows, className="table"),
            html.H4("Extended facts and media"),
            html.Div(dcc.Markdown(facts_html), style={"border": "1px solid #ddd", "padding": "10px"}),
            html.Br(),
            dbc.Button("Back to diagram", id="btn-back", color="secondary")
        ])
        return detail

    # back button clears detail
    @app.callback(
        Output("detail-container", "children"),
        Input("btn-back", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_detail(_):
        return ""

    return app

# -------------------------
# main entry point
# -------------------------
def main() -> None:
    """
    Run the Dash development server.

    This function is the single entry point for running the program.
    """
    app = create_dash_app()
    # run server suitable for Deepnote or local preview
    app.run_server(debug=True, port=8050, host="0.0.0.0")

if __name__ == "__main__":
    main()
