import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# Lorentz transformation function
def lorentz_transform(t, x, v):
    gamma = 1 / np.sqrt(1 - v**2)
    t_prime = gamma * (t - v * x)
    x_prime = gamma * (x - v * t)
    return t_prime, x_prime

# Generate a fixed grid for reference
time_range = np.linspace(-5, 5, 11)
space_range = np.linspace(-5, 5, 11)

# Create the initial plot layout
def create_figure(velocity=0.5, points=None, color='purple', size=8):
    if points is None:
        points = []

    fig = go.Figure()

    # Constant background grid in light gray (untransformed)
    for t in time_range:
        fig.add_trace(go.Scatter(x=space_range, y=[t]*len(space_range), mode='lines', line=dict(color='lightgray', width=0.5), showlegend=False))
    for x in space_range:
        fig.add_trace(go.Scatter(x=[x]*len(time_range), y=time_range, mode='lines', line=dict(color='lightgray', width=0.5), showlegend=False))

    # Transformed grid lines in red and blue
    for t in time_range:
        t_transformed, x_transformed = lorentz_transform(t * np.ones_like(space_range), space_range, velocity)
        fig.add_trace(go.Scatter(x=x_transformed, y=t_transformed, mode='lines', line=dict(color='red', width=1), showlegend=False))

    for x in space_range:
        t_transformed, x_transformed = lorentz_transform(time_range, x * np.ones_like(time_range), velocity)
        fig.add_trace(go.Scatter(x=x_transformed, y=t_transformed, mode='lines', line=dict(color='blue', width=1), showlegend=False))

    # Add light cones
    time_values = np.linspace(-5, 5, 100)
    fig.add_trace(go.Scatter(x=time_values, y=time_values, mode="lines", line=dict(dash="dash", color="green"), showlegend=False))
    fig.add_trace(go.Scatter(x=time_values, y=-time_values, mode="lines", line=dict(dash="dash", color="green"), showlegend=False))

    # Plot each transformed point
    for x_point, t_point in points:
        t_transformed, x_transformed = lorentz_transform(t_point, x_point, velocity)
        fig.add_trace(go.Scatter(x=[x_transformed], y=[t_transformed], mode="markers", marker=dict(color=color, size=size), showlegend=False))

    # Layout adjustments
    fig.update_layout(
        xaxis_title="Space (x)",
        yaxis_title="Time (t)",
        xaxis=dict(range=[-5, 5], autorange=False),
        yaxis=dict(range=[-5, 5], autorange=False),
        title=f"Lorentz Transformation with Relative Velocity = {velocity:.2f}c",
        dragmode="pan"
    )
    
    return fig

# App layout
app.layout = html.Div([
    html.H1("Interactive Lorentz Transformation Tool with Grid-Aligned Points"),
    
    # Velocity slider
    html.Label("Relative Velocity (as fraction of speed of light, c)"),
    dcc.Slider(id='velocity-slider', min=-0.99, max=0.99, step=0.01, value=0.5, marks={-0.99: '-0.99', 0: '0', 0.99: '0.99'}),
    
    # Color picker and size selector for points
    html.Label("Point Color"),
    dcc.Input(id='point-color', type='text', value='purple'),
    html.Label("Point Size"),
    dcc.Input(id='point-size', type='number', value=8),
    
    # Graph display
    dcc.Graph(id='lorentz-graph', config={'scrollZoom': True}),
    
    # Hidden div to store clicked points
    dcc.Store(id='points-storage', data=[])
])

# Callback to update the figure based on user inputs
@app.callback(
    Output('lorentz-graph', 'figure'),
    Output('points-storage', 'data'),
    Input('velocity-slider', 'value'),
    Input('lorentz-graph', 'clickData'),
    Input('point-color', 'value'),
    Input('point-size', 'value'),
    State('points-storage', 'data')
)
def update_graph(velocity, click_data, color, size, points):
    # Initialize points list if empty
    if points is None:
        points = []

    # Process clickData to add or remove points at grid intersections
    if click_data:
        click_x = click_data['points'][0]['x']
        click_y = click_data['points'][0]['y']
        
        # Snap click to nearest grid intersection (original, untransformed coordinates)
        snap_x = round(click_x)
        snap_y = round(click_y)

        # Toggle the point: add if not in list, remove if already present
        clicked_point = (snap_x, snap_y)
        if clicked_point in points:
            points.remove(clicked_point)  # Remove point if it's already plotted
        else:
            points.append(clicked_point)  # Add point if not already plotted

    # Create updated figure with transformed points
    fig = create_figure(velocity, points, color, size)
    return fig, points

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
