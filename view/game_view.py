import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import arcade
import settings
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from menus.pause_menu import PauseMenu
from view.field import PixelField
from view.ball import Ball


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.time = 0
        self.paused = False
        self.music = None
        self.time_text = arcade.Text(
            "Время: 0",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )

        self.pause_menu = PauseMenu(
            on_continue=self.resume,
            on_menu=self.go_to_menu,
            on_settings=self.go_to_settings
        )
        self.field = PixelField(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ball = Ball(self.field.center[0], self.field.center[1])

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self._start_music()
        if self.paused:
            self.pause_menu.manager.enable()
        else:
            self.pause_menu.manager.disable()

    def _start_music(self):
        if self.music is None:
            self.music = arcade.Sound(settings.MUSIC_PATH, streaming=True)
        if settings.MUSIC_PLAYER is None:
            settings.MUSIC_PLAYER = self.music.play(
                volume=settings.SOUND_VOLUME,
                loop=True
            )

    def _stop_music(self):
        if settings.MUSIC_PLAYER is not None:
            settings.MUSIC_PLAYER.pause()
            settings.MUSIC_PLAYER = None

    def on_hide_view(self):
        self.pause_menu.manager.disable()
        self._stop_music()

    def on_update(self, delta_time):
        if not self.paused:
            self.time += delta_time
            self.time_text.text = f"Время: {int(self.time)}"
            if self.ball:
                self.ball.update(delta_time, self.field.bounds)

    def on_draw(self):
        self.clear()

        self.field.draw()
        if self.ball:
            self.ball.draw()

        self.time_text.draw()

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
        self.paused = True
        self.pause_menu.manager.disable()
        self.window.show_view(Setting_Menu_View(return_view=self))
