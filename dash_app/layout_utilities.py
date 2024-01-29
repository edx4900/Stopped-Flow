from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dcc

def create_sidebar(key):
    # Define your sidebar layout here using Dash Bootstrap Components
    sidebar = html.Div(
        [
            html.Button("Open Experiment Panel", id="open-sidebar", n_clicks=0),
            dbc.Offcanvas(
                html.P(
                    "Experiments will go here"
                ),
                id="offcanvas",
                title="Experiments",
                is_open=False,
                placement="start",
            ),
        ],
        className="d-flex justify-content-end",
    )
    return sidebar

def create_dropdowns(key):
    substrates = key['substrate'].unique().tolist()
    substrates.sort()
    
    dropdowns = html.Div([
        "Substrate:",
        dcc.Dropdown(
            id='substrate-dropdown',
            options=[{'label': s, 'value': s} for s in substrates],
            placeholder='Select a substrate'
        ),
        "pH:",
        dcc.Dropdown(id='ph-dropdown', placeholder='Select pH'),
        "Solvent:",
        dcc.Dropdown(id='solvent-dropdown', placeholder='Select a solvent'),
        "Substrate Concentration:",
        dcc.Dropdown(id='substrate-concentration-dropdown', placeholder='Select substrate concentration'),
    ], style={'margin-bottom': '20px'})
    
    return dropdowns

def create_plots():
    plots = html.Div([
        html.Div([
            dcc.Graph(id='plot-area'),
            dcc.Checklist(
                id='baseline-toggle',
                options=[{'label': 'Toggle Baseline', 'value': 'baseline'}],
                value=[],
                style={'position': 'absolute', 'top': '50px', 'right': '10px', 'zIndex': '1000'}
            ),
            html.Div([
                html.Button('◀', id='previous-button', disabled=True, style={'margin-right': '5px'}),
                html.Span(id='plot-info', children='', style={'display': 'none', 'margin-right': '5px', 'margin-left': '5px'}),
                html.Button('▶', id='next-button', disabled=True, style={'margin-left': '5px'})
            ], style={'text-align': 'center', 'margin-top': '10px'})

        ], style={'position': 'relative'}),
        
        html.Div([
            dcc.Input(id='wavelength-input', type='number', placeholder='Enter a wavelength', disabled=True),
            html.Button('Add Wavelength Trace', id='add-wavelength-button', disabled=True),
            dcc.Graph(id='wavelength-plot-area'),
            html.Button('Log Time Scale', id='toggle-x-axis', n_clicks=0, disabled=True),
        ], style={'text-align': 'center', 'margin-top': '50px'})
    ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'margin-bottom': '20px'})

    return plots

def create_sliders():
    sliders = html.Div([
        html.Label('Time Range:'),
        dcc.RangeSlider(id='time-slider', min=0, max=1, value=[0, 1], step=0.01, marks={0: '0', 1: '1'}, disabled=True),
        html.Label('Time Step:'),
        dcc.Slider(id='time-step-slider', min=1, max=100, value=10, step=10, disabled=True)
    ], style={'margin-bottom': '20px'})

    return sliders