from dash import dcc, html
from dash_app.layout_utilities import *
import dash_bootstrap_components as dbc

def create_layout(key):
    layout = html.Div([
        dcc.Store(id='current-index', data={'index': 0}),  # Store for current experiment index
        create_sidebar(key),
        dbc.Container([
            dcc.Store(id='baseline-flag', data={'baseline': False}),  # Store for baseline flag
            create_dropdowns(key),
            create_plots(),
            create_sliders(),
        ], fluid=True),
    ])

    return layout