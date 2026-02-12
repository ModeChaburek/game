import os
import sys
import random

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import arcade
import settings
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from menus.pause_menu import PauseMenu
from view.field import PixelField
from view.ball import Ball
from view.player import Player


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
        self.players = self._create_players()

    def _team_colors(self):
        options = settings.TEAM_COLOR_OPTIONS
        if not options:
            return arcade.color.BLUE, arcade.color.RED

        blue_index = settings.TEAM_BLUE_COLOR_INDEX % len(options)
        red_index = settings.TEAM_RED_COLOR_INDEX % len(options)
        if len(options) > 1 and blue_index == red_index:
            red_index = (red_index + 1) % len(options)

        return options[blue_index][1], options[red_index][1]

    def _spawn_bounds(self, side, radius):
        left, right, bottom, top = self.field.bounds
        mid_x = (left + right) / 2
        margin = radius * 2

        if side == "left":
            x_min = left + radius + margin
            x_max = mid_x - radius - margin
        else:
            x_min = mid_x + radius + margin
            x_max = right - radius - margin

        y_min = bottom + radius + margin
        y_max = top - radius - margin

        if x_max <= x_min:
            if side == "left":
                x_min = left + radius
                x_max = mid_x - radius
            else:
                x_min = mid_x + radius
                x_max = right - radius

        if y_max <= y_min:
            y_min = bottom + radius
            y_max = top - radius

        return x_min, x_max, y_min, y_max

    def _in_center_circle(self, x, y, radius):
        center_x, center_y = self.field.center
        exclude_radius = self.field.center_circle_radius + radius
        dx = x - center_x
        dy = y - center_y
        return (dx * dx + dy * dy) <= (exclude_radius * exclude_radius)

    def _random_positions(self, side, count, radius):
        x_min, x_max, y_min, y_max = self._spawn_bounds(side, radius)
        if x_max <= x_min or y_max <= y_min:
            return []

        min_distance = radius * 20 + 1
        min_distance_sq = min_distance * min_distance
        positions = []
        attempts = 0
        max_attempts = 5000

        while len(positions) < count and attempts < max_attempts:
            attempts += 1
            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)
            if self._in_center_circle(x, y, radius):
                continue
            if all(
                (x - px) ** 2 + (y - py) ** 2 > min_distance_sq
                for px, py in positions
            ):
                positions.append((x, y))

        if len(positions) < count:
            positions = self._grid_positions(
                x_min, x_max, y_min, y_max, count, min_distance, radius
            )

        return positions

    def _grid_positions(self, x_min, x_max, y_min, y_max, count, spacing, radius):
        if spacing <= 0:
            return []

        x_positions = []
        current_x = x_min
        while current_x <= x_max:
            x_positions.append(current_x)
            current_x += spacing

        y_positions = []
        current_y = y_min
        while current_y <= y_max:
            y_positions.append(current_y)
            current_y += spacing

        candidates = [
            (x, y)
            for x in x_positions
            for y in y_positions
            if not self._in_center_circle(x, y, radius)
        ]
        random.shuffle(candidates)
        return candidates[:count]

    def _create_players(self):
        numbers = random.sample(range(1, 100), 10)
        blue_numbers = numbers[:5]
        red_numbers = numbers[5:]

        players = []
        blue_color, red_color = self._team_colors()

        max_radius = 18
        min_radius = 4
        chosen_radius = min_radius
        blue_positions = []
        red_positions = []

        for radius in range(max_radius, min_radius - 1, -1):
            blue_positions = self._random_positions("left", 5, radius)
            red_positions = self._random_positions("right", 5, radius)
            if len(blue_positions) == 5 and len(red_positions) == 5:
                chosen_radius = radius
                break

        for (x, y), number in zip(blue_positions, blue_numbers):
            players.append(Player(x, y, chosen_radius, blue_color, number))

        for (x, y), number in zip(red_positions, red_numbers):
            players.append(Player(x, y, chosen_radius, red_color, number))

        return players

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
        for player in self.players:
            player.draw()
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
