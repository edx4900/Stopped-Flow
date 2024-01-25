from dash import html
import dash_bootstrap_components as dbc

def create_sidebar():
    # Define your sidebar layout here using Dash Bootstrap Components
    sidebar = dbc.Offcanvas(
        [
            html.H2("Sidebar", className="display-4"),
            html.Hr(),
            html.P(
                "A simple sidebar layout with navigation links", className="lead"
            ),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact"),
                    # Add more navigation links as needed for your app
                ],
                vertical=True,
                pills=True,
            ),
            # Add other sidebar components like dropdowns and buttons here
        ],
        id="offcanvas",
        title="Sidebar",
        is_open=False,
    )
    return sidebar