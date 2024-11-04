import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, lambdify, sympify

# Title of the app
st.title("Interactive Lorentz Transformation Tool with 2D/3D Options and Curve Plotting")

# Sidebar for mode selection (2D or 3D)
mode = st.sidebar.selectbox("Choose mode", ("2D", "3D"))

# Sidebar for velocity input
st.sidebar.header("Lorentz Transformation Controls")

# 2D Mode Velocity Input
if mode == "2D":
    velocity_slider = st.sidebar.slider("Relative Velocity (as a fraction of the speed of light, c)", -0.99, 0.99, 0.5)
    velocity_input = st.sidebar.number_input("Or enter velocity directly:", min_value=-0.99, max_value=0.99, value=velocity_slider, step=0.01)
    velocity = velocity_input if velocity_input != velocity_slider else velocity_slider

# 3D Mode Velocity Input
else:
    # Velocity components input for 3D (as fractions of the speed of light)
    v_x_slider = st.sidebar.slider("Velocity in X direction (as a fraction of c)", -0.99, 0.99, 0.5)
    v_x_input = st.sidebar.number_input("Or enter v_x directly:", min_value=-0.99, max_value=0.99, value=v_x_slider, step=0.01)
    v_x = v_x_input if v_x_input != v_x_slider else v_x_slider

    v_y_slider = st.sidebar.slider("Velocity in Y direction (as a fraction of c)", -0.99, 0.99, 0.0)
    v_y_input = st.sidebar.number_input("Or enter v_y directly:", min_value=-0.99, max_value=0.99, value=v_y_slider, step=0.01)
    v_y = v_y_input if v_y_input != v_y_slider else v_y_slider

    # Check total velocity magnitude
    velocity_magnitude = np.sqrt(v_x**2 + v_y**2)
    if velocity_magnitude >= 1:
        st.error("The total velocity must be less than the speed of light (|v| < c).")
        st.stop()

# Lorentz transformation functions for 2D and 3D
def lorentz_transform(t, x, v):
    gamma = 1 / np.sqrt(1 - v**2)
    t_prime = gamma * (t - v * x)
    x_prime = gamma * (x - v * t)
    return t_prime, x_prime

def lorentz_transform_3d(t, x, y, v_x, v_y):
    gamma = 1 / np.sqrt(1 - (v_x**2 + v_y**2))
    t_prime = gamma * (t - v_x * x - v_y * y)
    x_prime = gamma * (x - v_x * t)
    y_prime = gamma * (y - v_y * t)
    return t_prime, x_prime, y_prime

# Grid line generation functions for 2D
def generate_grid_lines_2d(velocity):
    grid_lines = []
    time_range = np.linspace(-5, 5, 11)
    space_range = np.linspace(-5, 5, 11)
    for t in time_range:
        t_transformed, x_transformed = lorentz_transform(t * np.ones_like(space_range), space_range, velocity)
        grid_lines.append(go.Scatter(x=x_transformed, y=t_transformed, mode='lines', line=dict(color='red', width=1), showlegend=False))
    for x in space_range:
        t_transformed, x_transformed = lorentz_transform(time_range, x * np.ones_like(time_range), velocity)
        grid_lines.append(go.Scatter(x=x_transformed, y=t_transformed, mode='lines', line=dict(color='blue', width=1), showlegend=False))
    return grid_lines

# Grid line generation functions for 3D
def generate_grid_lines_3d(v_x, v_y):
    grid_lines = []
    time_range = np.linspace(-5, 5, 6)
    space_range = np.linspace(-5, 5, 6)
    for t in time_range:
        for y in space_range:
            t_transformed, x_transformed, y_transformed = lorentz_transform_3d(
                t * np.ones_like(space_range), space_range, y * np.ones_like(space_range), v_x, v_y
            )
            grid_lines.append(go.Scatter3d(
                x=x_transformed, 
                y=y_transformed, 
                z=t_transformed, 
                mode='lines', 
                line=dict(color='red', width=1), 
                showlegend=False
            ))

    for t in time_range:
        for x in space_range:
            t_transformed, x_transformed, y_transformed = lorentz_transform_3d(
                t * np.ones_like(space_range), 
                x * np.ones_like(space_range), 
                space_range,
                v_x, v_y
            )
            grid_lines.append(go.Scatter3d(
                x=x_transformed, 
                y=y_transformed, 
                z=t_transformed, 
                mode='lines', 
                line=dict(color='blue', width=1), 
                showlegend=False
            ))

    for x in space_range:
        for y in space_range:
            t_transformed, x_transformed, y_transformed = lorentz_transform_3d(
                time_range, 
                x * np.ones_like(time_range), 
                y * np.ones_like(time_range),
                v_x, v_y
            )
            grid_lines.append(go.Scatter3d(
                x=x_transformed, 
                y=y_transformed, 
                z=t_transformed, 
                mode='lines', 
                line=dict(color='green', width=1), 
                showlegend=False
            ))

    return grid_lines

# Points data management
if 'points' not in st.session_state:
    st.session_state['points'] = []

# Add points based on mode
st.sidebar.subheader("Add Points")
if mode == "2D":
    x_coord = st.sidebar.number_input("X-coordinate", min_value=-5.0, max_value=5.0, step=0.5)
    t_coord = st.sidebar.number_input("T-coordinate", min_value=-5.0, max_value=5.0, step=0.5)
    point_color = st.sidebar.color_picker("Choose Point Color", "#800080")
    if st.sidebar.button("Add Point"):
        new_point = (x_coord, t_coord, point_color)
        if new_point not in st.session_state['points']:
            st.session_state['points'].append(new_point)
else:
    x_coord = st.sidebar.number_input("X-coordinate", min_value=-5.0, max_value=5.0, step=0.5)
    y_coord = st.sidebar.number_input("Y-coordinate", min_value=-5.0, max_value=5.0, step=0.5)
    t_coord = st.sidebar.number_input("T-coordinate", min_value=-5.0, max_value=5.0, step=0.5)
    point_color = st.sidebar.color_picker("Choose Point Color", "#800080")
    if st.sidebar.button("Add Point"):
        new_point = (x_coord, y_coord, t_coord, point_color)
        if new_point not in st.session_state['points']:
            st.session_state['points'].append(new_point)

# Curve plotting section for 2D mode
if mode == "2D":
    enable_curve = st.sidebar.checkbox("Enable Curve Plotting")
    if enable_curve:
        st.sidebar.subheader("Add Curve")
        curve_expr = st.sidebar.text_input("Enter curve expression in terms of x (e.g., x**2 + 2*x + 3)", "x**2")
        curve_color = st.sidebar.color_picker("Choose Curve Color", "#FF00FF")
        x = symbols('x')
        try:
            if curve_expr.strip():
                curve_function = lambdify(x, sympify(curve_expr), modules=['numpy'])
                x_vals = np.linspace(-5, 5, 100)
                y_vals = curve_function(x_vals)
                t_transformed, x_transformed = lorentz_transform(y_vals, x_vals, velocity)
                curve_trace = go.Scatter(x=x_transformed, y=t_transformed, mode="lines", line=dict(color=curve_color, width=2), name="Transformed Curve")
            else:
                curve_trace = None
        except Exception as e:
            st.error(f"Could not plot curve '{curve_expr}': {e}")
            curve_trace = None
    else:
        curve_trace = None
else:
    curve_trace = None

# Generate and display plot based on mode
if mode == "2D":
    plot_data = generate_grid_lines_2d(velocity)
    if curve_trace:
        plot_data.append(curve_trace)
    for x_point, t_point, color in [p for p in st.session_state['points'] if len(p) == 3]:
        t_transformed, x_transformed = lorentz_transform(t_point, x_point, velocity)
        plot_data.append(go.Scatter(x=[x_transformed], y=[t_transformed], mode="markers", marker=dict(color=color, size=10), showlegend=False))
    fig = go.Figure(data=plot_data, layout=go.Layout(
        xaxis=dict(title="Space (x)", range=[-5, 5]), yaxis=dict(title="Time (t)", range=[-5, 5]), dragmode="pan"
    ))
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    # Description for 2D mode
    st.write("## Lorentz Transformation Tool - 2D Mode")
    st.write("""
    This tool visualizes the 2D Lorentz transformation for an observer moving along the x-axis.
    
    - Adjust the velocity to see how it affects the 2D spacetime grid.
    - Add points to observe their transformed coordinates.
    - Enable curve plotting to visualize the Lorentz-transformed curve.
    - The **red and blue grid lines** represent transformed lines of constant time and space.
    - The **green dashed lines** represent the light cone (\(x = \pm t\)).
    """)

else:
    plot_data = generate_grid_lines_3d(v_x, v_y)
    for x_point, y_point, t_point, color in [p for p in st.session_state['points'] if len(p) == 4]:
        t_transformed, x_transformed, y_transformed = lorentz_transform_3d(t_point, x_point, y_point, v_x, v_y)
        plot_data.append(go.Scatter3d(
            x=[x_transformed], y=[y_transformed], z=[t_transformed], mode="markers",
            marker=dict(color=color, size=5), showlegend=False
        ))

    fig = go.Figure(data=plot_data, layout=go.Layout(
        scene=dict(
            xaxis=dict(title="Space (x)", range=[-5, 5]),
            yaxis=dict(title="Space (y)", range=[-5, 5]),
            zaxis=dict(title="Time (t)", range=[-5, 5])
        ),
        title=f"3D Lorentz Transformation with Velocity Components v_x = {v_x:.2f}c, v_y = {v_y:.2f}c"
    ))
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    # Description for 3D mode
    st.write("## Lorentz Transformation Tool - 3D Mode")
    st.write("""
    This tool visualizes the 3D Lorentz transformation for an observer moving with components of velocity along the x and y axes.
    
    - Adjust the x and y velocity components to see how they affect the 3D spacetime grid.
    - Add points to observe their transformed coordinates.
    - The **red, blue, and green grid lines** represent transformed lines of constant time in the 3D spacetime.
    """)
