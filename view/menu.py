import arcade
from arcade.gui import *
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from view.game_view import GameView
from view.setting_view import Setting_Menu_View


class MenuView(arcade.View):

    def __init__(self):
        super().__init__()  # ← ОБЯЗАТЕЛЬНО

        arcade.set_background_color(arcade.color.GRAY)

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        play_button = UIFlatButton(
            text="Играть",
            width=200
        )

        setting_button = UIFlatButton(
            text="Настройки",
            width=200
        )

        exit_button = UIFlatButton(
            text="Выйти",
            width=200
        )

        @play_button.event("on_click")
        def on_play_click(event):
            game_view = GameView()
            self.window.show_view(game_view)
            print("Играть нажато")

        @setting_button.event("on_click")
        def on_settings_click(event):
            setting_menu_view = Setting_Menu_View()
            self.window.show_view(setting_menu_view)
            print("Настройки")

        @exit_button.event("on_click")
        def on_exit_click(event):
            arcade.close_window()

        self.box_layout.add(play_button)
        self.box_layout.add(setting_button)
        self.box_layout.add(exit_button)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "Basket Random",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 200,
            arcade.color.PINK,
            font_size=64,
            anchor_x="center",
            anchor_y="center"
        )

        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

