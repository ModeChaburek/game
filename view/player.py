import arcade
import math


class Player:
    def __init__(self, center_x, center_y, radius, color, number, team):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.number = number
        self.team = team
        self.velocity = [0.0, 0.0]
        self.friction = 250.0
        self.stop_threshold = 8.0
        self.mass = 2.0
        self.movable = False
        self.score = 0

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

    def reset_position(self, x, y):
        self.center_x = x
        self.center_y = y
        self.velocity[0] = 0.0
        self.velocity[1] = 0.0
        self.movable = False

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

        self.center_x += self.velocity[0] * delta_time
        self.center_y += self.velocity[1] * delta_time

        left, right, bottom, top = bounds

        if self.center_x - self.radius < left:
            self.center_x = left + self.radius
            self.velocity[0] = abs(self.velocity[0])
        if self.center_x + self.radius > right:
            self.center_x = right - self.radius
            self.velocity[0] = -abs(self.velocity[0])
        if self.center_y - self.radius < bottom:
            self.center_y = bottom + self.radius
            self.velocity[1] = abs(self.velocity[1])
        if self.center_y + self.radius > top:
            self.center_y = top - self.radius
            self.velocity[1] = -abs(self.velocity[1])

        self._apply_friction(delta_time)

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x,
            self.center_y,
            self.radius,
            self.color
        )
        arcade.draw_circle_outline(
            self.center_x,
            self.center_y,
            self.radius,
            arcade.color.BLACK,
            2
        )
        font_size = max(10, int(self.radius * 0.9))
        arcade.draw_text(
            str(self.number),
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            font_size=font_size,
            anchor_x="center",
            anchor_y="center"
        )
