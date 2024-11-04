import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, lambdify, sympify

# Title of the app
st.title("Interactive Lorentz Transformation Tool with Optional Curve Plotting")

# Sidebar for velocity input
st.sidebar.header("Lorentz Transformation Controls")

# Velocity input options: slider and text box
velocity_slider = st.sidebar.slider("Relative Velocity (as a fraction of the speed of light, c)", -0.99, 0.99, 0.5)
velocity_input = st.sidebar.number_input("Or enter velocity directly:", min_value=-0.99, max_value=0.99, value=velocity_slider, step=0.01)
velocity = velocity_input if velocity_input != velocity_slider else velocity_slider

# Lorentz transformation function
def lorentz_transform(t, x, v):
    gamma = 1 / np.sqrt(1 - v**2)
    t_prime = gamma * (t - v * x)
    x_prime = gamma * (x - v * t)
    return t_prime, x_prime

# Function to generate transformed grid lines
def generate_transformed_grid_lines(velocity):
    grid_lines = []
    time_range = np.linspace(-5, 5, 11)
    space_range = np.linspace(-5, 5, 11)

    # Transformed grid lines in red and blue
    for t in time_range:
        t_transformed, x_transformed = lorentz_transform(t * np.ones_like(space_range), space_range, velocity)
        grid_lines.append(go.Scatter(x=x_transformed, y=t_transformed, mode='lines', line=dict(color='red', width=1), showlegend=False))

    for x in space_range:
        t_transformed, x_transformed = lorentz_transform(time_range, x * np.ones_like(time_range), velocity)
        grid_lines.append(go.Scatter(x=x_transformed, y=t_transformed, mode='lines', line=dict(color='blue', width=1), showlegend=False))

    return grid_lines

# Function to generate fixed vertical reference grid lines and original axes with gray highlight
def generate_reference_grid():
    grid_lines = []
    time_range = np.linspace(-5, 5, 11)
    space_range = np.linspace(-5, 5, 11)

    # Vertical and horizontal gray reference lines for static frame
    for x in space_range:
        grid_lines.append(go.Scatter(x=x * np.ones_like(time_range), y=time_range, mode='lines', line=dict(color='lightgray', width=0.5), showlegend=False))
    for t in time_range:
        grid_lines.append(go.Scatter(x=space_range, y=t * np.ones_like(space_range), mode='lines', line=dict(color='lightgray', width=0.5), showlegend=False))

    return grid_lines

# Function to generate transformed frame axes with yellow highlight
def generate_transformed_axes(velocity):
    # Transformed t'-axis (x=0)
    t_range = np.linspace(-5, 5, 100)
    t_prime, x_prime = lorentz_transform(t_range, np.zeros_like(t_range), velocity)
    transformed_axes = [
        go.Scatter(x=x_prime, y=t_prime, mode='lines', line=dict(color='rgba(255, 255, 0, 0.3)', width=10), showlegend=False),
        go.Scatter(x=x_prime, y=t_prime, mode='lines', line=dict(color='red', width=2, dash='dash'), name="Transformed t'-axis")
    ]

    # Transformed x'-axis (t=0)
    x_range = np.linspace(-5, 5, 100)
    t_prime, x_prime = lorentz_transform(np.zeros_like(x_range), x_range, velocity)
    transformed_axes.append(go.Scatter(x=x_prime, y=t_prime, mode='lines', line=dict(color='rgba(255, 255, 0, 0.3)', width=10), showlegend=False))
    transformed_axes.append(go.Scatter(x=x_prime, y=t_prime, mode='lines', line=dict(color='blue', width=2, dash='dash'), name="Transformed x'-axis"))
    
    return transformed_axes

# Points data
if 'points' not in st.session_state:
    st.session_state['points'] = {}  # Dictionary to store points by coordinates (x, t): color

# Input for adding new points
st.sidebar.subheader("Add Points")
x_coord = st.sidebar.number_input("X-coordinate", min_value=-5.0, max_value=5.0, step=0.5, key="x_coord")
t_coord = st.sidebar.number_input("T-coordinate", min_value=-5.0, max_value=5.0, step=0.5, key="t_coord")
point_color = st.sidebar.color_picker("Choose Point Color", "#800080")

# Button to add or update the point with the selected color
if st.sidebar.button("Add/Update Point"):
    st.session_state['points'][(x_coord, t_coord)] = point_color  # Update color if point exists, else add new

# Dropdown to select and remove points
st.sidebar.subheader("Remove Points")
point_to_remove = st.sidebar.selectbox("Select a point to remove", [(x, t) for (x, t) in st.session_state['points']])
if st.sidebar.button("Remove Selected Point"):
    if (point_to_remove[0], point_to_remove[1]) in st.session_state['points']:
        del st.session_state['points'][(point_to_remove[0], point_to_remove[1])]

# Button to clear all points
if st.sidebar.button("Clear All Points"):
    st.session_state['points'] = {}

# Curve plotting section with enable option
enable_curve = st.sidebar.checkbox("Enable Curve Plotting")
if enable_curve:
    st.sidebar.subheader("Add Curve")
    curve_expr = st.sidebar.text_input("Enter curve expression in terms of x (e.g., x**2 + 2*x + 3)", "x**2")
    curve_color = st.sidebar.color_picker("Choose Curve Color", "#FF00FF")

    # Define symbols
    x = symbols('x')

    # Try to generate the curve
    try:
        if curve_expr.strip():  # Only try if there's an input
            # Convert the user input to a sympy expression and create a lambda function for it
            curve_function = lambdify(x, sympify(curve_expr), modules=['numpy'])
            x_vals = np.linspace(-5, 5, 100)
            y_vals = curve_function(x_vals)
            
            # Apply Lorentz transformation to curve points
            t_transformed, x_transformed = lorentz_transform(y_vals, x_vals, velocity)

            # Plot the transformed curve
            curve_trace = go.Scatter(x=x_transformed, y=t_transformed, mode="lines", line=dict(color=curve_color, width=2), name="Transformed Curve")
        else:
            curve_trace = None
    except Exception as e:
        st.error(f"Could not plot curve '{curve_expr}': {e}")
        curve_trace = None
else:
    curve_trace = None  # Disable curve plotting if unchecked

# Generate plot data with transformed grid and reference grid
plot_data = generate_reference_grid() + generate_transformed_grid_lines(velocity) + generate_transformed_axes(velocity)

# Add the curve if successfully created
if curve_trace:
    plot_data.append(curve_trace)

# Transform and plot each point with its color
for (x_point, t_point), color in st.session_state['points'].items():
    t_transformed, x_transformed = lorentz_transform(t_point, x_point, velocity)
    plot_data.append(go.Scatter(x=[x_transformed], y=[t_transformed], mode="markers", marker=dict(color=color, size=10), showlegend=False))

# Add light cones (x=t and x=-t lines)
time_range = np.linspace(-5, 5, 100)
plot_data.append(go.Scatter(x=time_range, y=time_range, mode="lines", line=dict(dash="dash", color="green"), name="Light cone (x = t)"))
plot_data.append(go.Scatter(x=time_range, y=-time_range, mode="lines", line=dict(dash="dash", color="green"), name="Light cone (x = -t)"))

# Configure Plotly layout
layout = go.Layout(
    xaxis=dict(title="Space (x)", range=[-5, 5], fixedrange=False),
    yaxis=dict(title="Time (t)", range=[-5, 5], fixedrange=False),
    title=f"Lorentz Transformation with Relative Velocity = {velocity:.2f}c",
    dragmode="pan"
)

# Display plot in Streamlit
fig = go.Figure(data=plot_data, layout=layout)
st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# Explanation
st.write("## Lorentz Transformation Tool with Optional Curve Plotting")
st.write("""
This tool visualizes the Lorentz transformation for an observer moving at a relative velocity \(v\) (as a fraction of the speed of light \(c\)) along the \(x\)-axis.

- Enter a curve expression in the form of `x**2 + 2*x + 3` (using Python-style `**` for powers) if curve plotting is enabled.
- Adjust the velocity to see how the Lorentz transformation affects the grid, points, and optional curve.
- The **red and blue grid lines** show the Lorentz-transformed coordinates of constant time \(t'\) and constant position \(x'\).
- The **green dashed lines** represent the light cone (\(x = \pm t\)).
""")
