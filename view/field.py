import math
import arcade


class PixelField:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tiles = []
        self.field_rect = None
        self.center_line = None
        self.center_circle_radius = 0
        self.center_dot_radius = 0
        self.penalty_boxes = []
        self.goal_boxes = []
        self.penalty_spots = []
        self.line_color = (245, 245, 245)
        self.line_width = 4
        self.goal_highlight_color = (255, 230, 120, 80)
        self.bounds = None
        self.center = (screen_width / 2, screen_height / 2)
        self._build()

    def _build(self):
        tile_size = 16
        field_width = self.screen_width
        field_height = self.screen_height

        field_left = 0
        field_bottom = 0
        field_right = field_left + field_width
        field_top = field_bottom + field_height

        self.tiles = []
        self.penalty_boxes = []
        self.goal_boxes = []
        self.penalty_spots = []
        self.bounds = (field_left, field_right, field_bottom, field_top)

        grass_light = (40, 160, 70)
        grass_dark = (34, 140, 62)
        stripe_tiles = 3

        cols = int(math.ceil(field_width / tile_size))
        rows = int(math.ceil(field_height / tile_size))

        for row in range(rows):
            for col in range(cols):
                stripe = (col // stripe_tiles) % 2
                color = grass_light if stripe == 0 else grass_dark
                x = field_left + col * tile_size
                y = field_bottom + row * tile_size
                self.tiles.append(
                    (x + tile_size / 2, y + tile_size / 2, tile_size, color)
                )

        center_x = (field_left + field_right) / 2
        center_y = (field_bottom + field_top) / 2
        self.center = (center_x, center_y)

        self.field_rect = (center_x, center_y, field_width, field_height)
        self.center_line = (center_x, field_bottom, center_x, field_top)

        circle_diam = min(field_width, field_height) * 0.3
        self.center_circle_radius = circle_diam / 2
        self.center_dot_radius = self.line_width * 0.75

        penalty_depth = field_width * 0.18
        penalty_height = field_height * 0.5
        goal_depth = field_width * 0.06
        goal_height = field_height * 0.3

        for side in ("left", "right"):
            if side == "left":
                box_center_x = field_left + penalty_depth / 2
                goal_center_x = field_left + goal_depth / 2
                spot_x = field_left + penalty_depth * 0.65
            else:
                box_center_x = field_right - penalty_depth / 2
                goal_center_x = field_right - goal_depth / 2
                spot_x = field_right - penalty_depth * 0.65

            self.penalty_boxes.append(
                (box_center_x, center_y, penalty_depth, penalty_height)
            )
            self.goal_boxes.append(
                (goal_center_x, center_y, goal_depth, goal_height)
            )
            self.penalty_spots.append((spot_x, center_y))

    def draw(self):
        for center_x, center_y, size, color in self.tiles:
            arcade.draw_lbwh_rectangle_filled(
                center_x - size / 2,
                center_y - size / 2,
                size,
                size,
                color
            )

        if self.field_rect:
            left = self.field_rect[0] - self.field_rect[2] / 2
            bottom = self.field_rect[1] - self.field_rect[3] / 2
            arcade.draw_lbwh_rectangle_outline(
                left,
                bottom,
                self.field_rect[2],
                self.field_rect[3],
                self.line_color,
                self.line_width
            )
        if self.center_line:
            arcade.draw_line(
                self.center_line[0],
                self.center_line[1],
                self.center_line[2],
                self.center_line[3],
                self.line_color,
                self.line_width
            )
        if self.center_circle_radius > 0:
            arcade.draw_circle_outline(
                self.field_rect[0],
                self.field_rect[1],
                self.center_circle_radius,
                self.line_color,
                self.line_width
            )
        if self.center_dot_radius > 0:
            arcade.draw_circle_filled(
                self.field_rect[0],
                self.field_rect[1],
                self.center_dot_radius,
                self.line_color
            )

        for box in self.penalty_boxes:
            left = box[0] - box[2] / 2
            bottom = box[1] - box[3] / 2
            arcade.draw_lbwh_rectangle_outline(
                left,
                bottom,
                box[2],
                box[3],
                self.line_color,
                self.line_width
            )
        for box in self.goal_boxes:
            left = box[0] - box[2] / 2
            bottom = box[1] - box[3] / 2
            arcade.draw_lbwh_rectangle_filled(
                left,
                bottom,
                box[2],
                box[3],
                self.goal_highlight_color
            )
        for box in self.goal_boxes:
            left = box[0] - box[2] / 2
            bottom = box[1] - box[3] / 2
            arcade.draw_lbwh_rectangle_outline(
                left,
                bottom,
                box[2],
                box[3],
                self.line_color,
                self.line_width
            )
        for spot in self.penalty_spots:
            arcade.draw_circle_filled(
                spot[0],
                spot[1],
                self.center_dot_radius,
                self.line_color
            )
