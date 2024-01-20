from SF_analysis_processing import *
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

def plot_wavelength_vs_intensity_dash(key, substrate, pH=None, substrate_concentration=None, solvent=None, index=None, time_step=10, time_cutoff=None, specified_wavelengths=None, subtract_baseline_flag=False, wavelength_plotting_range=None, start_time=None):
    # Build the criteria dictionary with only non-None values
    criteria = {'substrate': substrate, 'pH': pH, 'substrate_concentration': substrate_concentration, 'solvent': solvent}

    # Fetch experiments based on the criteria
    experiments = get_experiments_by_criteria(key, **criteria)

    if experiments.empty or index is None or index >= len(experiments):
        return go.Figure()  # Return an empty figure if no valid experiment is found

    fig = go.Figure()

    # Select the specific experiment based on the index
    experiment = experiments.iloc[index]

    # Get push number and date for the title
    push_number = experiment.get('push', 'Unknown')
    experiment_date = experiment.get('date', 'Unknown Date')

    data = experiment['data']
    data['Time'] = pd.to_numeric(data['Time'], errors='coerce')
    data.dropna(subset=['Time'], inplace=True)

    # Baseline Subtraction if enabled
    if subtract_baseline_flag:
        baseline = find_baseline_for_push(key, experiment['push'])
        if baseline is not None:
            data = subtract_baseline(data, baseline)

    # Apply time cutoff and filtering
    if time_cutoff is not None or start_time is not None:
        data = filter_by_time_cutoff(data, time_cutoff, start_time)

    if not data.empty:
        time_min = data['Time'].min()
        time_max = data['Time'].max()
        time_points = data['Time'].unique()
        selected_time_points = time_points[::time_step]

        # Determine wavelength range
        wavelength_columns = [col for col in data.columns if col != 'Time']
        if wavelength_plotting_range is not None:
            first_wavelength, last_wavelength = wavelength_plotting_range
            wavelength_columns = [col for col in wavelength_columns if first_wavelength <= float(col) <= last_wavelength]
        else:
            first_wavelength = float(wavelength_columns[0])
            last_wavelength = float(wavelength_columns[-1])

        # Viridis color scale
        color_scale = px.colors.sequential.Viridis

        # Plotting data for each time point
        for time_point in selected_time_points:
            time_point_data = data[data['Time'] == time_point][wavelength_columns]
            color_value = (time_point - time_min) / (time_max - time_min)  # Normalize time value for color scale
            color = color_scale[int(color_value * (len(color_scale) - 1))]  # Map to color scale
            fig.add_trace(go.Scatter(
                x=time_point_data.columns.astype(float),
                y=time_point_data.iloc[0].values,
                mode='lines',
                line=dict(color=color, width=2),
                showlegend=False  # Hide individual line legends
            ))

        # Add a separate scatter trace for the color bar
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(
                colorscale='Viridis',
                cmin=time_min,
                cmax=time_max,
                colorbar=dict(title="Time"),
                size=10
            ),
            hoverinfo='none',  # Hide hover info
            showlegend=False  # Ensure this trace does not appear in the legend
        ))

    # Customize the layout of the Plotly figure
    fig.update_layout(
        title=f"Experiment: {push_number} (Date: {experiment_date})",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Intensity",
        xaxis=dict(range=[first_wavelength, last_wavelength]),
    )

    return fig