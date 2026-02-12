import arcade


class Ball:
    def __init__(self, center_x, center_y, radius=20, color=arcade.color.WHITE):
        self.radius = radius
        self.color_white = arcade.color.WHITE
        self.color_black = arcade.color.BLACK
        self.sprite = arcade.SpriteCircle(radius, color)
        self.sprite.center_x = center_x
        self.sprite.center_y = center_y
        self.velocity = [0.0, 0.0]
        self.movable = False

    def update(self, delta_time, bounds):
        if not self.movable:
            return
        if bounds is None:
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

    def draw(self):
        cx = self.sprite.center_x
        cy = self.sprite.center_y
        arcade.draw_circle_filled(cx, cy, self.radius, self.color_white)
        arcade.draw_circle_outline(cx, cy, self.radius, self.color_black, 2)
        spot_radius = max(2, int(self.radius * 0.25))
        offset = self.radius * 0.45
        arcade.draw_circle_filled(cx - offset, cy, spot_radius, self.color_black)
        arcade.draw_circle_filled(cx + offset, cy, spot_radius, self.color_black)
        arcade.draw_circle_filled(cx, cy + offset, spot_radius, self.color_black)
