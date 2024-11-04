import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Title of the app
st.title("Interactive Lorentz Transformation Tool with Custom Point Alignment")

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

# Function to generate grid lines
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

# Function to generate fixed vertical reference grid lines
def generate_reference_grid():
    grid_lines = []
    time_range = np.linspace(-5, 5, 11)
    space_range = np.linspace(-5, 5, 11)

    # Vertical gray reference lines (untransformed)
    for x in space_range:
        grid_lines.append(go.Scatter(x=x * np.ones_like(time_range), y=time_range, mode='lines', line=dict(color='lightgray', width=0.5), showlegend=False))
    
    return grid_lines

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

# Custom alignment of points
st.sidebar.subheader("Align Points with Time Axis")
if len(st.session_state['points']) >= 2:
    points_list = [(i, f"Point {i+1} ({x}, {t})") for i, (x, t) in enumerate(st.session_state['points'].keys())]
    selected_points = st.sidebar.multiselect("Select two points to align:", points_list, max_selections=2)
    
    if len(selected_points) == 2:
        index1, index2 = selected_points[0][0], selected_points[1][0]
        (x1, t1), (x2, t2) = list(st.session_state['points'].keys())[index1], list(st.session_state['points'].keys())[index2]
        
        # Calculate the required velocity to align selected points vertically
        def calculate_velocity_for_alignment(x1, t1, x2, t2):
            delta_x = x2 - x1
            delta_t = t2 - t1

            if delta_t == 0:
                st.error("The selected points have the same t-coordinate. Choose different points.")
                return None
            velocity = delta_x / delta_t

            if abs(velocity) >= 1:
                st.error("Calculated velocity exceeds the speed of light. Adjust point selection.")
                return None
            return velocity

        # Calculate velocity and apply if valid
        align_velocity = calculate_velocity_for_alignment(x1, t1, x2, t2)
        if align_velocity is not None:
            st.write(f"Calculated alignment velocity: {align_velocity:.2f}c")
            velocity = align_velocity

# Generate plot data with the (possibly adjusted) velocity
plot_data = generate_reference_grid() + generate_transformed_grid_lines(velocity)

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
st.write("## Lorentz Transformation Tool with Zoom and Pan")
st.write("""
This tool visualizes the Lorentz transformation for an observer moving at a relative velocity \(v\) (as a fraction of the speed of light \(c\)) along the \(x\)-axis.

- The gray vertical lines serve as reference lines that remain fixed, providing a frame to observe how the grid transforms.
- The red and blue grid lines show the Lorentz-transformed coordinates of constant time \(t'\) and constant position \(x'\).
- The green dashed lines represent the light cone (\(x = \pm t\)), representing the constant speed of light.
- Points can be added at specific \(x\) and \(t\) coordinates with chosen colors, and they will transform along with the grid as the velocity changes.
- **Custom Alignment**: Select two points to automatically align the line connecting them with the \(t\)-axis by adjusting the velocity.
""")
