import arcade
import math


class Ball:
    def __init__(self, center_x, center_y, radius=20, color=arcade.color.WHITE):
        self.radius = radius
        self.color_white = arcade.color.WHITE
        self.color_black = arcade.color.BLACK
        self.sprite = arcade.SpriteCircle(radius, color)
        self.sprite.center_x = center_x
        self.sprite.center_y = center_y
        self.velocity = [0.0, 0.0]
        self.friction = 240.0
        self.stop_threshold = 8.0
        self.mass = 0.8
        self.movable = False
        self.trail = []
        self.trail_max_len = 40

    @property
    def center_x(self):
        return self.sprite.center_x

    @center_x.setter
    def center_x(self, value):
        self.sprite.center_x = value

    @property
    def center_y(self):
        return self.sprite.center_y

    @center_y.setter
    def center_y(self, value):
        self.sprite.center_y = value

    def speed(self):
        return math.hypot(self.velocity[0], self.velocity[1])

    def is_moving(self):
        return self.movable

    def set_velocity(self, vx, vy):
        self.velocity[0] = vx
        self.velocity[1] = vy
        self.refresh_movable()

    def refresh_movable(self):
        self.movable = self.speed() > self.stop_threshold

    def reset(self, center_x, center_y):
        self.sprite.center_x = center_x
        self.sprite.center_y = center_y
        self.velocity[0] = 0.0
        self.velocity[1] = 0.0
        self.movable = False
        self.trail = []

    def _apply_friction(self, delta_time):
        speed = self.speed()
        if speed <= self.stop_threshold:
            self.velocity[0] = 0.0
            self.velocity[1] = 0.0
            self.movable = False
            return

        new_speed = max(0.0, speed - self.friction * delta_time)
        if new_speed <= self.stop_threshold:
            self.velocity[0] = 0.0
            self.velocity[1] = 0.0
            self.movable = False
            return

        scale = new_speed / speed
        self.velocity[0] *= scale
        self.velocity[1] *= scale
        self.movable = True

    def update(self, delta_time, bounds):
        if not self.movable or bounds is None:
            return

        self.sprite.center_x += self.velocity[0] * delta_time
        self.sprite.center_y += self.velocity[1] * delta_time

        left, right, bottom, top = bounds

        if self.sprite.left < left:
            self.sprite.left = left
            self.velocity[0] = abs(self.velocity[0])
        if self.sprite.right > right:
            self.sprite.right = right
            self.velocity[0] = -abs(self.velocity[0])
        if self.sprite.bottom < bottom:
            self.sprite.bottom = bottom
            self.velocity[1] = abs(self.velocity[1])
        if self.sprite.top > top:
            self.sprite.top = top
            self.velocity[1] = -abs(self.velocity[1])

        self._apply_friction(delta_time)
        self._append_trail()

    def _append_trail(self):
        self.trail.append((self.sprite.center_x, self.sprite.center_y))
        if len(self.trail) > self.trail_max_len:
            self.trail = self.trail[-self.trail_max_len :]

    def draw_trail(self):
        if len(self.trail) < 2:
            return
        color = (255, 255, 255, 90)
        if hasattr(arcade, "draw_line_strip"):
            arcade.draw_line_strip(self.trail, color, 2)
        else:
            arcade.draw_lines(self.trail, color, 2)

    def draw(self):
        self.draw_trail()
        cx = self.sprite.center_x
        cy = self.sprite.center_y
        arcade.draw_circle_filled(cx, cy, self.radius, self.color_white)
        arcade.draw_circle_outline(cx, cy, self.radius, self.color_black, 2)
        spot_radius = max(2, int(self.radius * 0.25))
        offset = self.radius * 0.45
        arcade.draw_circle_filled(cx - offset, cy, spot_radius, self.color_black)
        arcade.draw_circle_filled(cx + offset, cy, spot_radius, self.color_black)
        arcade.draw_circle_filled(cx, cy + offset, spot_radius, self.color_black)
