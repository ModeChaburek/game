import arcade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MenuView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Basket Random",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.PINK,
            font_size=64,
            anchor_x="center",
            anchor_y="center"
        )
