import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title of the app
st.title("Interactive Lorentz Transformation Tool with Movable Points")

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

# Generate grid of points for the main and background grids
time_range = np.linspace(-5, 5, 100)
space_range = np.linspace(-5, 5, 100)
t_grid, x_grid = np.meshgrid(time_range, space_range)

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))

# Plot the constant background grid (untransformed) in light gray
for t in np.linspace(-5, 5, 11):
    ax.plot(space_range, t * np.ones_like(space_range), color='lightgray', linestyle='-', linewidth=0.5)
for x in np.linspace(-5, 5, 11):
    ax.plot(x * np.ones_like(time_range), time_range, color='lightgray', linestyle='-', linewidth=0.5)

# Plot original axes
ax.axhline(0, color='k', linestyle='--', linewidth=1, label="Original t-axis")
ax.axvline(0, color='k', linestyle='--', linewidth=1, label="Original x-axis")

# Plot transformed grid lines for time and space
for t in np.linspace(-5, 5, 11):
    t_transformed, x_transformed = lorentz_transform(t * np.ones_like(space_range), space_range, velocity)
    ax.plot(x_transformed, t_transformed, color='red', alpha=0.5)

for x in np.linspace(-5, 5, 11):
    t_transformed, x_transformed = lorentz_transform(time_range, x * np.ones_like(time_range), velocity)
    ax.plot(x_transformed, t_transformed, color='blue', alpha=0.5)

# Plot light cones (45-degree lines where x = ±t)
ax.plot(time_range, time_range, color='green', linestyle='--', label="Light cone (x = t)")
ax.plot(time_range, -time_range, color='green', linestyle='--', label="Light cone (x = -t)")

# Initialize session state for points
if 'points' not in st.session_state:
    st.session_state['points'] = []  # Each point will be a tuple: (x, t, color)

# Input for adding new points
st.sidebar.subheader("Add Points")
x_coord = st.sidebar.number_input("X-coordinate", min_value=-5.0, max_value=5.0, step=0.5, key="x_coord")
t_coord = st.sidebar.number_input("T-coordinate", min_value=-5.0, max_value=5.0, step=0.5, key="t_coord")
point_color = st.sidebar.color_picker("Choose Point Color", "#800080")

# Button to add the point with the selected color
if st.sidebar.button("Add Point"):
    new_point = (x_coord, t_coord, point_color)
    if new_point not in st.session_state['points']:
        st.session_state['points'].append(new_point)  # Add new point with its color

# Dropdown to select and remove points
st.sidebar.subheader("Remove Points")
point_to_remove = st.sidebar.selectbox("Select a point to remove", [(p[0], p[1]) for p in st.session_state['points']])
if st.sidebar.button("Remove Selected Point"):
    st.session_state['points'] = [p for p in st.session_state['points'] if (p[0], p[1]) != point_to_remove]

# Button to clear all points
if st.sidebar.button("Clear All Points"):
    st.session_state['points'] = []

# Transform and plot each point with its color
for x_point, t_point, color in st.session_state['points']:
    # Apply Lorentz transformation to the points based on current velocity
    t_transformed, x_transformed = lorentz_transform(t_point, x_point, velocity)
    ax.plot(x_transformed, t_transformed, 'o', color=color, markersize=8)

# Set axis labels and limits
ax.set_xlabel("Space (x)")
ax.set_ylabel("Time (t)")
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.legend(loc="upper left")
ax.set_title(f"Lorentz Transformation with Relative Velocity = {velocity:.2f}c")

# Show the plot in Streamlit
st.pyplot(fig)

# Explanation
st.write("## Lorentz Transformation Tool with Movable Points")
st.write("""
This tool visualizes the Lorentz transformation for an observer moving at a relative velocity \(v\) (as a fraction of the speed of light \(c\)) along the \(x\)-axis.

- The light gray grid represents the **reference grid** at zero velocity, which remains fixed as a reference.
- The red lines represent the transformed grid lines of constant time \(t'\).
- The blue lines represent the transformed grid lines of constant position \(x'\).
- The green dashed lines represent the light cone (\(x = \pm t\)), which remains invariant, representing the constant speed of light.
- Points can be added to the graph with specific \(x\), \(t\) coordinates and color, and they will transform along with the grid.

Use the slider in the sidebar to adjust the relative velocity or enter it directly in the text box to observe how the coordinates are transformed relative to the reference grid.
""")
