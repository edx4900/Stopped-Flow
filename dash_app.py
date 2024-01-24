import pandas as pd
import plotting_dash
from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objs as go
import dash
import numpy as np

def create_dash_app(key):
    app = Dash(__name__)

    # Define initial options for the substrate dropdown
    substrates = key['substrate'].unique().tolist()
    substrates.sort()

    # Set up the app layout with grid layout
    app.layout = html.Div([
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
                dcc.Input(id='wavelength-input', type='number', placeholder='Enter a wavelength'),
                html.Button('Add Wavelength', id='add-wavelength-button'),
                dcc.Graph(id='wavelength-plot-area')
            ])
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

    
    # Callback to update dropdowns based on selected substrate
    @app.callback(
        [Output('ph-dropdown', 'options'),
         Output('solvent-dropdown', 'options'),
         Output('substrate-concentration-dropdown', 'options')],
        [Input('substrate-dropdown', 'value')]
    )
    def update_dropdowns(selected_substrate):
        if not selected_substrate:
            return [], [], []
        filtered_data = key[key['substrate'] == selected_substrate]
        
        ph_values = filtered_data['pH'].unique().tolist()
        ph_values.sort()
        ph_options = [{'label': ph, 'value': ph} for ph in ph_values]
        
        solvents = filtered_data['solvent'].unique().tolist()
        solvents.sort()
        solvent_options = [{'label': solvent, 'value': solvent} for solvent in solvents]
        
        concentrations = filtered_data['substrate_concentration'].unique().tolist()
        concentrations.sort()
        concentration_options = [{'label': c, 'value': c} for c in concentrations]
        
        return ph_options, solvent_options, concentration_options
    
    @app.callback(
        Output('baseline-flag', 'data'),
        [Input('baseline-toggle', 'value')]
    )
    def update_baseline_flag(toggle_value):
        return {'baseline': 'baseline' in toggle_value}
        
    @app.callback(
    [
        Output('plot-area', 'figure'),
        Output('current-index', 'data'),
        Output('previous-button', 'disabled'),
        Output('next-button', 'disabled'),
        Output('time-slider', 'min'),
        Output('time-slider', 'max'),
        Output('time-slider', 'value'),
        Output('time-slider', 'marks'),
        Output('time-slider', 'disabled'),
        Output('time-step-slider', 'disabled'),
        Output('plot-info', 'children'),
        Output('plot-info', 'style'),
    ],
    [
        Input('substrate-dropdown', 'value'),
        Input('ph-dropdown', 'value'),
        Input('solvent-dropdown', 'value'),
        Input('substrate-concentration-dropdown', 'value'),
        Input('previous-button', 'n_clicks'),
        Input('next-button', 'n_clicks'),
        Input('time-slider', 'value'),
        Input('time-step-slider', 'value'),
        Input('baseline-flag', 'data')
    ],
    State('current-index', 'data')
    )
    def update_plot(selected_substrate, selected_ph, selected_solvent, selected_concentration, prev_clicks, next_clicks, slider_value, time_step_value, baseline_flag_data, current_index_data):
        ctx = dash.callback_context
        current_index = current_index_data['index']

        # Initialize default states
        fig = go.Figure()
        disable_previous, disable_next, slider_disabled, time_step_slider_disabled = True, True, True, True
        min_time, max_time = 0, 1
        slider_marks = {0: '0', 1: '1'}
        plot_info_text, plot_info_style = '', {'display': 'none'}

        # Filter data based on selected conditions
        filtered_data = key[(key['substrate'] == selected_substrate) & 
                            (key['pH'] == selected_ph) & 
                            (key['solvent'] == selected_solvent) & 
                            (key['substrate_concentration'] == selected_concentration)]
        
        # Update index based on button clicks
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'previous-button' and current_index > 0:
                current_index -= 1
            elif button_id == 'next-button' and current_index < len(filtered_data) - 1:
                current_index += 1

        num_spectra = len(filtered_data)
        if num_spectra > 0:
            # Get the time range for the experiment
            time_range = plotting_dash.get_time_range_for_experiment(
                key, substrate=selected_substrate, pH=selected_ph, solvent=selected_solvent,
                substrate_concentration=selected_concentration, index=current_index
            )

            if time_range:
                min_time, max_time = time_range
                step = (int(max_time) - int(min_time)) // 10 or 1
                slider_marks = {i: str(i) for i in range(int(min_time), int(max_time) + 1, int(step))}
                slider_disabled = False

                if not ctx.triggered or (ctx.triggered and 'time-slider' not in button_id):
                    slider_value = [min_time, max_time]

            # Update plot based on the current experiment index and slider value
            fig = plotting_dash.plot_wavelength_vs_intensity_dash(
                key, substrate=selected_substrate, pH=selected_ph, solvent=selected_solvent,
                substrate_concentration=selected_concentration, time_range=slider_value,
                time_step=time_step_value, index=current_index, subtract_baseline_flag=baseline_flag_data['baseline']
            )

            disable_previous = current_index <= 0
            disable_next = current_index >= num_spectra - 1
            time_step_slider_disabled = False

            plot_info_text = f'{current_index + 1} of {num_spectra}'
            plot_info_style = {'display': 'inline'}
        else:
            # Reset current index if no data is available
            current_index = 0

        return fig, {'index': current_index}, disable_previous, disable_next, min_time, max_time, slider_value, slider_marks, slider_disabled, time_step_slider_disabled, plot_info_text, plot_info_style

    return app

def run_dash(key):
    app = create_dash_app(key)
    app.run_server(debug=True)
    # app.run(jupyter_mode="external")
