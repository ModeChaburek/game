import arcade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from menus.pause_menu import PauseMenu


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.time = 0
        self.paused = False

        self.pause_menu = PauseMenu(
            on_continue=self.resume,
            on_menu=self.go_to_menu,
            on_settings=self.go_to_settings
        )

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time):
        if not self.paused:
            self.time += delta_time

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            f"Время: {int(self.time)}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            40,
            anchor_x="center",
            anchor_y="center"
        )

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 180)
            )
            self.pause_menu.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            if self.paused:
                self.pause_menu.manager.enable()
            else:
                self.pause_menu.manager.disable()

    def resume(self):
        self.paused = False
        self.pause_menu.manager.disable()

    def go_to_menu(self):
        from view.menu import MenuView
        self.window.show_view(MenuView())

    def go_to_settings(self):
        from view.setting_view import Setting_Menu_View
        self.window.show_view(Setting_Menu_View())
