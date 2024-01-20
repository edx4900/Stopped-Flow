import pandas as pd
import plotting_dash
from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objs as go
import dash

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
        html.Button('Previous', id='previous-button', disabled=True),
        html.Button('Next', id='next-button', disabled=True)
    ])

    # Callback to update pH dropdown based on selected substrate
    @app.callback(
        Output('ph-dropdown', 'options'),
        Input('substrate-dropdown', 'value')
    )
    def update_dropdown(selected_substrate, column_name, output_id):
        if not selected_substrate:
            return []
        filtered_data = key[key['substrate'] == selected_substrate]
        values = filtered_data[column_name].unique().tolist()
        values.sort()
        return [{'label': value, 'value': value} for value in values]

    # Callback to update pH dropdown based on selected substrate
    @app.callback(
        Output('ph-dropdown', 'options'),
        Input('substrate-dropdown', 'value')
    )
    def update_ph_dropdown(selected_substrate):
        return update_dropdown(selected_substrate, 'pH', 'ph-dropdown')

    # Callback to update solvent dropdown based on selected substrate
    @app.callback(
        Output('solvent-dropdown', 'options'),
        Input('substrate-dropdown', 'value')
    )
    def update_solvent_dropdown(selected_substrate):
        return update_dropdown(selected_substrate, 'solvent', 'solvent-dropdown')

    # Callback to update substrate concentration dropdown based on selected substrate
    @app.callback(
        Output('substrate-concentration-dropdown', 'options'),
        Input('substrate-dropdown', 'value')
    )
    def update_concentration_dropdown(selected_substrate):
        return update_dropdown(selected_substrate, 'substrate_concentration', 'substrate-concentration-dropdown')
    # Modified callback to also control the disabled state of buttons
    @app.callback(
        [
            Output('plot-area', 'figure'),
            Output('current-index', 'data'),
            Output('previous-button', 'disabled'),
            Output('next-button', 'disabled')
        ],
        [
            Input('substrate-dropdown', 'value'),
            Input('ph-dropdown', 'value'),
            Input('solvent-dropdown', 'value'),
            Input('substrate-concentration-dropdown', 'value'),
            Input('previous-button', 'n_clicks'),
            Input('next-button', 'n_clicks')
        ],
    State('current-index', 'data')
    )
    def update_plot(selected_substrate, selected_ph, selected_solvent, selected_concentration, prev_clicks, next_clicks, current_index_data):
        ctx = dash.callback_context

        if not ctx.triggered or not selected_substrate or not selected_ph or not selected_solvent or not selected_concentration:
            # Return an empty figure, the current index, and default disabled states for the buttons
            return go.Figure(), current_index_data, True, True

        # Retrieve the current experiment index
        current_index = current_index_data['index']

        # Determine if navigation button was pressed
        if ctx.triggered[0]['prop_id'] == 'previous-button.n_clicks' and current_index > 0:
            current_index -= 1
        elif ctx.triggered[0]['prop_id'] == 'next-button.n_clicks':
            current_index += 1

        # Update plot based on the current experiment index
        # Assuming plotting_dash.plot_wavelength_vs_intensity_dash can handle an index parameter
        fig = plotting_dash.plot_wavelength_vs_intensity_dash(
            key,
            substrate=selected_substrate,
            pH=selected_ph,
            solvent=selected_solvent,
            substrate_concentration=selected_concentration,
            index=current_index  # Add index parameter to your plotting function
        )

        # Determine the number of available spectra
        num_spectra = len(key[(key['substrate'] == selected_substrate) & 
                            (key['pH'] == selected_ph) & 
                            (key['solvent'] == selected_solvent) & 
                            (key['substrate_concentration'] == selected_concentration)])

        # Determine if buttons should be disabled
        disable_previous = current_index <= 0
        disable_next = current_index >= num_spectra - 1

        return fig, {'index': current_index}, disable_previous, disable_next
    

    return app

def run_dash(key):
    app = create_dash_app(key)
    app.run_server(debug=True)
