from dash.dependencies import Input, Output, State
import dash
import plotly.graph_objs as go
import data_analysis.plotting_dash as plotting_dash

LAYOUT = go.Layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='rgb(255,255,255)'),
)

def register_callbacks(app, key):
# Add a callback to update the button text based on the current scale
    @app.callback(
        Output('toggle-x-axis', 'children'),
        [Input('x-axis-scale', 'children')]  # Depend on the x-axis scale state
    )
    def update_x_axis_button_text(current_scale):
        return 'Switch to Log Time Scale' if current_scale == 'linear' else 'Switch to Linear Time Scale'

    # Add a callback to update the scale based on the click
    @app.callback(
        Output('x-axis-scale', 'children'),
        [Input('toggle-x-axis', 'n_clicks')],
        [State('x-axis-scale', 'children')]
    )
    def toggle_x_axis_scale(n_clicks, current_scale):
        if n_clicks is None or n_clicks == 0:  # Handle the initial state where n_clicks could be None or 0
            return 'linear'  # Default to linear scale

        # Toggle between 'linear' and 'log' scale based on the current scale
        return 'log' if current_scale == 'linear' else 'linear'
    
    @app.callback(
        Output('toggle-x-axis', 'disabled'),
        [Input('wavelength-input', 'value')]

    )
    def enable_time_toggle(wavelengths_str):
        # Enable the toggle button if wavelengths_str is not None or empty
        return not wavelengths_str

        
    @app.callback(
        Output("offcanvas", "is_open"),
        Input("open-sidebar", "n_clicks"),
        [State("offcanvas", "is_open")],
    )
    def toggle_offcanvas(n1, is_open):
        if n1:
            return not is_open
        return is_open
    

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
        [Output('wavelength-input', 'disabled')],
        [Input('plot-area', 'figure')],
        [State('substrate-dropdown', 'value'),
        State('ph-dropdown', 'value'),
        State('solvent-dropdown', 'value'),
        State('substrate-concentration-dropdown', 'value')]
    )
    def enable_wavelength_input(plot_figure, selected_substrate, selected_ph, selected_solvent, selected_concentration):
        # Check if data is available for plotting
        data_available = False
        if selected_substrate and selected_ph and selected_solvent and selected_concentration:
            # Assuming 'key' is accessible here, or pass it as an argument
            filtered_data = key[(key['substrate'] == selected_substrate) &
                                (key['pH'] == selected_ph) &
                                (key['solvent'] == selected_solvent) &
                                (key['substrate_concentration'] == selected_concentration)]
            data_available = not filtered_data.empty

        # Enable input and button if data is available
        return not data_available, 
    
    
    # Callback to handle wavelength input and update the subplot
    @app.callback(
        Output('wavelength-plot-area', 'figure'),
        [
            Input('wavelength-input', 'value'),
            Input('substrate-dropdown', 'value'),
            Input('ph-dropdown', 'value'),
            Input('solvent-dropdown', 'value'),
            Input('substrate-concentration-dropdown', 'value'),
            Input('time-slider', 'value'),
            Input('baseline-flag', 'data'),
            Input('x-axis-scale', 'children')
        ],
        [State('current-index', 'data')]  # Get the current x-axis scale from the hidden Div
    )
    def update_wavelength_plot(wavelengths_str, selected_substrate, selected_ph, selected_solvent, selected_concentration, slider_value, baseline_flag_data, xaxis_scale, current_index_data):
    # Rest of existing callback code...
        fig = go.Figure(layout=LAYOUT)
        current_index = current_index_data['index']
        filtered_data = key[(key['substrate'] == selected_substrate) & 
                            (key['pH'] == selected_ph) & 
                            (key['solvent'] == selected_solvent) & 
                            (key['substrate_concentration'] == selected_concentration)]

        if not filtered_data.empty and wavelengths_str:
            # Split the wavelengths string into a list
            wavelengths = [float(w.strip()) for w in wavelengths_str.split(',') if w.strip()]
            current_entry = filtered_data.iloc[current_index]
            current_push = current_entry['push']

            # Determine the x-axis scale based on the toggle button text
            fig = plotting_dash.plot_specified_wavelength_traces(key, current_push, wavelengths, start_time=slider_value[0], time_cutoff=slider_value[1], xaxis_type=xaxis_scale)

        return fig


    # Callback to update the wavelength vs. intensity time course plot    
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
        fig = go.Figure(layout=LAYOUT)
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

