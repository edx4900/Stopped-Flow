from dash import dcc, html
from dash_app.sidebar import create_sidebar

def create_layout(key):
    # initialize sidebar
    sidebar = create_sidebar()
    # Define initial options for the substrate dropdown
    substrates = key['substrate'].unique().tolist()
    substrates.sort()

    # Set up the app layout with grid layout
    layout = html.Div([
        dcc.Store(id='current-index', data={'index': 0}),  # Store for current experiment index

        # Row for the controls (excluding sliders, baseline toggle, and navigation buttons)
        html.Div([
            dcc.Dropdown(id='substrate-dropdown', options=[{'label': s, 'value': s} for s in substrates], placeholder='Select a substrate'),
            dcc.Dropdown(id='ph-dropdown', placeholder='Select pH'),
            dcc.Dropdown(id='solvent-dropdown', placeholder='Select a solvent'),
            dcc.Dropdown(id='substrate-concentration-dropdown', placeholder='Select substrate concentration'),
        ], style={'margin-bottom': '20px'}),

        # Grid for the plots with the baseline toggle and navigation buttons overlay
        html.Div([
            html.Div([
                dcc.Graph(id='plot-area'),
                dcc.Checklist(
                    id='baseline-toggle',
                    options=[{'label': 'Toggle Baseline', 'value': 'baseline'}],
                    value=[],
                    style={'position': 'absolute', 'top': '50px', 'right': '10px', 'zIndex': '1000'}
                ),
                # Update the navigation buttons with initial hidden plot info
                html.Div([
                    html.Button('◀', id='previous-button', disabled=True, style={'margin-right': '5px'}),
                    html.Span(id='plot-info', children='', style={'display': 'none', 'margin-right': '5px', 'margin-left': '5px'}),
                    html.Button('▶', id='next-button', disabled=True, style={'margin-left': '5px'})
                ], style={'text-align': 'center', 'margin-top': '10px'})

            ], style={'position': 'relative'}),
            
            html.Div([
                dcc.Input(id='wavelength-input', type='number', placeholder='Enter a wavelength', disabled=True),
                html.Button('Add Wavelength Trace', id='add-wavelength-button', disabled=True),
                dcc.Graph(id='wavelength-plot-area')
            ], style={'text-align': 'center', 'margin-top': '50px'})
        ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'margin-bottom': '20px'}),

        # Row for the sliders
        html.Div([
            html.Label('Time Range:'),
            dcc.RangeSlider(id='time-slider', min=0, max=1, value=[0, 1], step=0.01, marks={0: '0', 1: '1'}, disabled=True),
            html.Label('Time Step:'),
            dcc.Slider(id='time-step-slider', min=1, max=100, value=10, step=10, disabled=True)
        ], style={'margin-bottom': '20px'}),

        dcc.Store(id='baseline-flag', data={'baseline': False}),  # Store for baseline flag
    ])

    return layout