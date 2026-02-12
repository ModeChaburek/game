import arcade


class Player:
    def __init__(self, center_x, center_y, radius, color, number):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.number = number

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
