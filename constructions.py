"""
This file will draw out the problem and the various constructions that might be done when solving the problem.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np


def plot(
    points: dict[str, tuple[float, float]],
    lines: dict[str, tuple[float, float, float]],
    circles: dict[str, tuple[float, float, float]],
):
    _, ax = plt.subplots()
    ax.axis("off")

    # Set aspect ratio to be equal
    ax.set_aspect("equal", adjustable="datalim")

    # Draw the points!
    plt.plot(
        [p[0] for p in points.values()],
        [p[1] for p in points.values()],
        "o",
    )
    for label, (x, y) in points.items():
        ax.text(x, y, label, fontsize=12, ha="right", va="bottom")

    # Draw the circles!
    for cx, cy, r in circles.values():
        circle = Circle((cx, cy), r, fill=False)
        ax.add_patch(circle)

    # Draw the lines!
    # NOTE(edward): Lines can potentially go on forever, so to avoid rendering
    # lines outside of the axis, we take into account xlim and ylim. We want to
    # make sure to render everything else (points and circles) beforehand to
    # ensure these axis limits reflect the latest state of our construction.
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    for a, b, c in lines.values():
        # ax + by + c = 0
        boundary_points = []

        # Intersections with vertical boundaries (x = x_min, x_max)
        if abs(b) > 0:
            x_vals = np.array(xlim)
            y_vals = -(a * x_vals + c) / b
            valid_mask = (y_vals >= ylim[0]) & (y_vals <= ylim[1])
            boundary_points.extend(zip(x_vals[valid_mask], y_vals[valid_mask]))

        # Intersections with horizontal boundaries (y = y_min, y_max)
        if abs(a) > 0:
            y_vals = np.array(ylim)
            x_vals = -(b * y_vals + c) / a
            valid_mask = (x_vals >= xlim[0]) & (x_vals <= xlim[1])
            boundary_points.extend(zip(x_vals[valid_mask], y_vals[valid_mask]))

        # Draw line if we have at least 2 unique intersection points
        if len(boundary_points) >= 2:
            unique_points = list(set(boundary_points))
            if len(unique_points) >= 2:
                p1, p2 = unique_points[:2]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linewidth=1)

    plt.show()
