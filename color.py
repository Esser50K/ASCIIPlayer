import curses
import numpy as np
import math
from functools import lru_cache


class CursesColor:
    def __init__(self, start_color_idx=0):
        """
        Precompute a palette of custom colors that spans the RGB space as evenly as possible.
        Colors will be defined in the curses range (0–1000) and paired with a color pair id.
        """
        if not curses.has_colors():
            raise RuntimeError("Curses does not support colors")
        if not curses.can_change_color():
            raise RuntimeError("Terminal cannot change colors")

        self.start_color_idx = start_color_idx
        self.max_color_idx = curses.COLORS
        self.num_custom_colors = self.max_color_idx - self.start_color_idx
        if self.num_custom_colors < 1:
            raise RuntimeError("No custom color slots available.")

        # Determine how many steps per channel are needed.
        # We want the total number of grid points to be close to num_custom_colors.
        steps = math.ceil(self.num_custom_colors ** (1 / 3))

        # Generate a full grid for each channel using np.linspace.
        # The values will be in the 0–1000 range.
        r_vals = np.linspace(0, 1000, steps, endpoint=True)
        g_vals = np.linspace(0, 1000, steps, endpoint=True)
        b_vals = np.linspace(0, 1000, steps, endpoint=True)
        full_grid = []
        for r in r_vals:
            for g in g_vals:
                for b in b_vals:
                    full_grid.append((int(r), int(g), int(b)))
        total_grid = len(full_grid)

        # If the grid has more colors than available slots, sample uniformly.
        if total_grid > self.num_custom_colors:
            # Compute spacing such that we select exactly num_custom_colors colors.
            spacing = (total_grid - 1) / (self.num_custom_colors -
                                          1) if self.num_custom_colors > 1 else 1
            palette = [full_grid[int(round(i * spacing))]
                       for i in range(self.num_custom_colors)]
        else:
            palette = full_grid

        # Now initialize each custom color and its color pair.
        # List of tuples: (color (tuple), custom_color_idx, pair_id)
        self.palette = []
        current_color_idx = self.start_color_idx
        current_pair_id = 1  # Color pair IDs start at 1
        for color in palette:
            curses.init_color(current_color_idx, color[0], color[1], color[2])
            curses.init_pair(current_pair_id, current_color_idx, -1)
            self.palette.append((color, current_color_idx, current_pair_id))
            current_color_idx += 1
            current_pair_id += 1

    @lru_cache(maxsize=255 * 255 * 255)
    def get_color(self, bgr: tuple) -> int:
        """
        Given an RGB color (assumed 0-255 per channel),
        scale it to 0-1000 and return the curses color pair id from the palette
        that is the closest match.
        """
        # Convert the input (0-255) to curses scale (0-1000)
        b, g, r = bgr
        target = ((r * 1000) // 255,
                  (g * 1000) // 255,
                  (b * 1000) // 255)

        # Find the closest color in the palette (using Euclidean distance)
        best_distance = None
        best_pair = None
        for color, custom_idx, pair_id in self.palette:
            dr = color[0] - target[0]
            dg = color[1] - target[1]
            db = color[2] - target[2]
            distance = dr * dr + dg * dg + db * db
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_pair = pair_id

        return best_pair
