import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title of the app
st.title("Interactive Lorentz Transformation Tool")

# Sidebar for velocity input
st.sidebar.header("Lorentz Transformation Controls")
velocity = st.sidebar.slider("Relative Velocity (as a fraction of the speed of light, c)", -0.99, 0.99, 0.5)
st.sidebar.write("Velocity chosen:", velocity, "c")

# Lorentz transformation function
def lorentz_transform(t, x, v):
    gamma = 1 / np.sqrt(1 - v**2)
    t_prime = gamma * (t - v * x)
    x_prime = gamma * (x - v * t)
    return t_prime, x_prime

# Generate grid of points
time_range = np.linspace(-5, 5, 100)
space_range = np.linspace(-5, 5, 100)
t_grid, x_grid = np.meshgrid(time_range, space_range)

# Apply Lorentz transformation to the grid of points
t_prime_grid, x_prime_grid = lorentz_transform(t_grid, x_grid, velocity)

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))

# Plot original axes
ax.axhline(0, color='k', linestyle='--', linewidth=1, label="Original t-axis")
ax.axvline(0, color='k', linestyle='--', linewidth=1, label="Original x-axis")

# Plot transformed grid lines for t and x
for t in np.linspace(-5, 5, 11):
    t_transformed, x_transformed = lorentz_transform(t * np.ones_like(space_range), space_range, velocity)
    ax.plot(x_transformed, t_transformed, color='red', alpha=0.5)

for x in np.linspace(-5, 5, 11):
    t_transformed, x_transformed = lorentz_transform(time_range, x * np.ones_like(time_range), velocity)
    ax.plot(x_transformed, t_transformed, color='blue', alpha=0.5)

# Plot light cones (45-degree lines where x = ±t)
ax.plot(time_range, time_range, color='green', linestyle='--', label="Light cone (x = t)")
ax.plot(time_range, -time_range, color='green', linestyle='--', label="Light cone (x = -t)")

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
st.write("## Lorentz Transformation Tool")
st.write("""
This interactive tool visualizes the Lorentz transformation for an observer moving at a relative velocity \(v\) (as a fraction of the speed of light \(c\)) along the \(x\)-axis.

- The red lines represent the transformed grid lines of constant time \(t'\).
- The blue lines represent the transformed grid lines of constant position \(x'\).
- The green dashed lines represent the light cone (\(x = \pm t\)), which remains invariant, representing the constant speed of light.

Use the slider in the sidebar to adjust the relative velocity and observe how the coordinates are transformed.
""")
