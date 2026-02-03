import arcade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MenuView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "БАСКЕТ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            font_size=64,
            anchor_x="center",
            anchor_y="center"
        )
