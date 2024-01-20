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

    # Set up the app layout
    app.layout = html.Div([
        dcc.Store(id='current-index', data={'index': 0}),  # Store for current experiment index
        dcc.Dropdown(id='substrate-dropdown', options=[{'label': s, 'value': s} for s in substrates], placeholder='Select a substrate'),
        dcc.Dropdown(id='ph-dropdown', placeholder='Select pH'),
        dcc.Dropdown(id='solvent-dropdown', placeholder='Select a solvent'),
        dcc.Dropdown(id='substrate-concentration-dropdown', placeholder='Select substrate concentration'),
        dcc.Graph(id='plot-area'),
        dcc.RangeSlider(id='time-slider', min=0, max=1, value=[0, 1], step=0.01, marks={0: '0', 1: '1'}, disabled=True),
        html.Button('Previous', id='previous-button', disabled=True),
        html.Button('Next', id='next-button', disabled=True)
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
        [
            Output('plot-area', 'figure'),
            Output('current-index', 'data'),
            Output('previous-button', 'disabled'),
            Output('next-button', 'disabled'),
            Output('time-slider', 'min'),
            Output('time-slider', 'max'),
            Output('time-slider', 'value'),
            Output('time-slider', 'marks'),
            Output('time-slider', 'disabled')
        ],
        [
            Input('substrate-dropdown', 'value'),
            Input('ph-dropdown', 'value'),
            Input('solvent-dropdown', 'value'),
            Input('substrate-concentration-dropdown', 'value'),
            Input('previous-button', 'n_clicks'),
            Input('next-button', 'n_clicks'),
            Input('time-slider', 'value')
        ],
        State('current-index', 'data')
    )
    def update_plot(selected_substrate, selected_ph, selected_solvent, selected_concentration, prev_clicks, next_clicks, slider_value, current_index_data):
        ctx = dash.callback_context

        # Initialize an empty figure and default values for the slider
        fig = go.Figure()
        min_time = 0
        max_time = 1
        slider_marks = {0: '0', 1: '1'}
        slider_disabled = True

        # Retrieve the current experiment index
        current_index = current_index_data['index']

        # Determine if navigation button was pressed
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'previous-button' and current_index > 0:
                current_index -= 1
            elif button_id == 'next-button':
                current_index += 1

        # Check if all dropdowns have a value selected
        if selected_substrate and selected_ph and selected_solvent and selected_concentration:
            # Get the time range for the experiment
            time_range = plotting_dash.get_time_range_for_experiment(
                key,
                substrate=selected_substrate,
                pH=selected_ph,
                solvent=selected_solvent,
                substrate_concentration=selected_concentration,
                index=current_index
            )

            if time_range:
                min_time, max_time = time_range
                # Adjust the slider marks based on the time range to avoid clutter
                step = (int(max_time) - int(min_time)) // 10 or 1
                slider_marks = {i: str(i) for i in range(int(min_time), int(max_time) + 1, int(step))}
                slider_disabled = False

                # Only update slider_value if the dropdowns or navigation buttons triggered the callback
                if not ctx.triggered or (ctx.triggered and 'time-slider' not in button_id):
                    slider_value = [min_time, max_time]

            # Update plot based on the current experiment index and slider value
            fig = plotting_dash.plot_wavelength_vs_intensity_dash(
                key,
                substrate=selected_substrate,
                pH=selected_ph,
                solvent=selected_solvent,
                substrate_concentration=selected_concentration,
                time_range=slider_value,  # Pass the slider value as the time range
                index=current_index
            )

        # Determine the number of available spectra
        num_spectra = len(key[(key['substrate'] == selected_substrate) & 
                            (key['pH'] == selected_ph) & 
                            (key['solvent'] == selected_solvent) & 
                            (key['substrate_concentration'] == selected_concentration)])

        # Determine if buttons should be disabled
        disable_previous = current_index <= 0
        disable_next = current_index >= num_spectra - 1

        # Return the updated figure, index data, button states, and time slider properties
        return fig, {'index': current_index}, disable_previous, disable_next, min_time, max_time, slider_value, slider_marks, slider_disabled

    return app

def run_dash(key):
    app = create_dash_app(key)
    app.run_server(debug=True)
