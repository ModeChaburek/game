import os
import sys
import random
import math

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
from view import physics
from view import locale


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

        self.teams = ("blue", "red")
        self.turn_index = 0
        self.current_team = self.teams[self.turn_index]
        self.selected_player = None
        self.shot_in_progress = False
        self.aim_position = None
        self.shot_power = 4.0
        self.shot_max_speed = 650.0
        self.ball_max_speed = 900.0
        self.player_max_speed = 720.0
        self.max_substeps = 6
        self.players_per_team = 8

        self.ball = Ball(self.field.center[0], self.field.center[1])
        self.max_move_per_step = max(8.0, self.ball.radius * 0.6)
        blue_color, red_color = self._team_colors()
        self.team_colors = {"blue": blue_color, "red": red_color}
        self.players = self._create_players(blue_color, red_color)

        self.scores = {"blue": 0, "red": 0}
        self.max_score = 3
        self.game_over = False
        self.winner_team = None
        self.last_shooter_team = None
        self.last_shooter_player = None
        self.goal_timer = 0.0

        self.turn_text = arcade.Text(
            "",
            10,
            SCREEN_HEIGHT - 20,
            arcade.color.WHITE,
            18,
            anchor_x="left",
            anchor_y="center"
        )
        self.status_text = arcade.Text(
            "",
            10,
            SCREEN_HEIGHT - 45,
            arcade.color.WHITE,
            14,
            anchor_x="left",
            anchor_y="center"
        )
        self.score_text = arcade.Text(
            "",
            10,
            SCREEN_HEIGHT - 70,
            arcade.color.WHITE,
            16,
            anchor_x="left",
            anchor_y="center"
        )
        self.goal_text = arcade.Text(
            locale.GOAL_TEXT,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.YELLOW,
            48,
            anchor_x="center",
            anchor_y="center"
        )
        self.winner_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 40,
            arcade.color.WHITE,
            36,
            anchor_x="center",
            anchor_y="center"
        )
        self.restart_text = arcade.Text(
            locale.RESTART_TEXT,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 20,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            anchor_y="center"
        )
        self._update_hud()

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
        margin = radius

        if side == "left":
            x_min = left + margin
            x_max = mid_x - margin
        else:
            x_min = mid_x + margin
            x_max = right - margin

        y_min = bottom + margin
        y_max = top - margin

        return x_min, x_max, y_min, y_max

    def _in_center_circle(self, x, y, radius):
        center_x, center_y = self.field.center
        exclude_radius = self.field.center_circle_radius + radius
        dx = x - center_x
        dy = y - center_y
        return (dx * dx + dy * dy) <= (exclude_radius * exclude_radius)

    def _random_positions(self, side, count, radius):
        x_min, x_max, y_min, y_max = self._spawn_bounds(side, radius)
        return self._positions_in_bounds(
            x_min,
            x_max,
            y_min,
            y_max,
            count,
            radius
        )

    def _positions_in_bounds(self, x_min, x_max, y_min, y_max, count, radius):
        if x_max <= x_min or y_max <= y_min:
            return []

        min_distance = radius * 2.4
        min_distance_sq = min_distance * min_distance
        positions = []
        attempts = 0
        max_attempts = 25000

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

    def _create_players(self, blue_color, red_color):
        total_players = self.players_per_team * 2
        numbers = random.sample(range(1, 100), total_players)
        blue_numbers = numbers[:self.players_per_team]
        red_numbers = numbers[self.players_per_team:]

        players = []

        target_radius = int(self.ball.radius * 0.75)
        max_radius = target_radius
        min_radius = 8
        chosen_radius = min_radius
        blue_positions = []
        red_positions = []

        for radius in range(max_radius, min_radius - 1, -1):
            for _ in range(6):
                blue_positions = self._random_positions("left", self.players_per_team, radius)
                red_positions = self._random_positions("right", self.players_per_team, radius)
                if len(blue_positions) == self.players_per_team and len(red_positions) == self.players_per_team:
                    chosen_radius = radius
                    break
            if len(blue_positions) == self.players_per_team and len(red_positions) == self.players_per_team:
                break

        for (x, y), number in zip(blue_positions, blue_numbers):
            players.append(Player(x, y, chosen_radius, blue_color, number, "blue"))

        for (x, y), number in zip(red_positions, red_numbers):
            players.append(Player(x, y, chosen_radius, red_color, number, "red"))

        return players

    def _update_hud(self):
        team_name = locale.TEAM_NAMES[self.current_team]
        self.turn_text.text = locale.TURN_LABEL.format(team=team_name)
        self.turn_text.color = self.team_colors[self.current_team]
        self.score_text.text = locale.SCORE_LABEL.format(
            blue=self.scores["blue"],
            red=self.scores["red"]
        )
        if self.game_over:
            winner_name = locale.TEAM_NAMES.get(self.winner_team, "")
            self.status_text.text = locale.WINNER_TEXT.format(team=winner_name)
        elif self.paused:
            self.status_text.text = locale.STATUS_PAUSE
        elif self.shot_in_progress:
            self.status_text.text = locale.STATUS_SHOT
        elif self.selected_player is None:
            self.status_text.text = locale.STATUS_SELECT_PLAYER.format(team=team_name)
        else:
            self.status_text.text = locale.STATUS_SELECT_TARGET

    def _player_at(self, x, y, team=None):
        for player in self.players:
            if team is not None and player.team != team:
                continue
            dx = x - player.center_x
            dy = y - player.center_y
            if dx * dx + dy * dy <= player.radius * player.radius:
                return player
        return None

    def _limit_entity_speed(self, entity, max_speed):
        vx, vy = physics.limit_speed(entity.velocity[0], entity.velocity[1], max_speed)
        entity.velocity[0] = vx
        entity.velocity[1] = vy
        entity.refresh_movable()

    def _start_shot(self, player, target_x, target_y):
        dx = target_x - player.center_x
        dy = target_y - player.center_y
        distance = math.hypot(dx, dy)
        if distance < 1:
            return False

        speed = min(self.shot_max_speed, distance * self.shot_power)
        vx = dx / distance * speed
        vy = dy / distance * speed
        player.set_velocity(vx, vy)
        self._limit_entity_speed(player, self.player_max_speed)
        self.last_shooter_team = player.team
        self.last_shooter_player = player
        self.shot_in_progress = True
        return True

    def _apply_player_ball_collision(self, player):
        if self.ball is None:
            return
        if not self.ball.is_moving() and not player.is_moving():
            return

        if physics.resolve_circle_collision(self.ball, player, restitution=0.85):
            self._limit_entity_speed(self.ball, self.ball_max_speed)
            self._limit_entity_speed(player, self.player_max_speed)

    def _apply_player_player_collisions(self):
        total = len(self.players)
        for i in range(total):
            for j in range(i + 1, total):
                if not self.players[i].is_moving() and not self.players[j].is_moving():
                    continue
                if physics.resolve_circle_collision(
                    self.players[i],
                    self.players[j],
                    restitution=0.6
                ):
                    self._limit_entity_speed(self.players[i], self.player_max_speed)
                    self._limit_entity_speed(self.players[j], self.player_max_speed)

    def _anything_moving(self):
        if self.ball and self.ball.is_moving():
            return True
        return any(player.is_moving() for player in self.players)

    def _advance_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.teams)
        self.current_team = self.teams[self.turn_index]
        self.selected_player = None
        self.aim_position = None
        self.shot_in_progress = False
        self._update_hud()

    def _reset_players_positions(self):
        if not self.players:
            return
        radius = self.players[0].radius
        blue_players = [p for p in self.players if p.team == "blue"]
        red_players = [p for p in self.players if p.team == "red"]

        blue_positions = self._random_positions("left", len(blue_players), radius)
        red_positions = self._random_positions("right", len(red_players), radius)
        if len(blue_positions) != len(blue_players) or len(red_positions) != len(red_players):
            return

        for player, (x, y) in zip(blue_players, blue_positions):
            player.reset_position(x, y)
        for player, (x, y) in zip(red_players, red_positions):
            player.reset_position(x, y)

    def _set_current_team(self, team):
        if team in self.teams:
            self.turn_index = self.teams.index(team)
            self.current_team = team

    def _reset_round(self, next_team):
        self.ball.reset(self.field.center[0], self.field.center[1])
        self._reset_players_positions()
        self.selected_player = None
        self.aim_position = None
        self.shot_in_progress = False
        self.last_shooter_team = None
        self.last_shooter_player = None
        self._set_current_team(next_team)
        self._update_hud()

    def _register_goal(self, scoring_team):
        if self.game_over:
            return
        self.scores[scoring_team] += 1
        if self.last_shooter_player and self.last_shooter_player.team == scoring_team:
            self.last_shooter_player.score += 1
        self.goal_timer = 1.4
        self.goal_text.text = f"{locale.GOAL_TEXT} {locale.TEAM_NAMES[scoring_team]}!"
        if self.scores[scoring_team] >= self.max_score:
            self._end_game(scoring_team)
            return
        next_team = "red" if scoring_team == "blue" else "blue"
        self._reset_round(next_team)

    def _check_goal(self):
        if self.ball is None:
            return False
        side = self.field.goal_side(self.ball.center_x, self.ball.center_y)
        if side is None:
            return False
        scoring_team = "red" if side == "left" else "blue"
        self._register_goal(scoring_team)
        return True

    def _end_game(self, winner_team):
        self.game_over = True
        self.winner_team = winner_team
        self.shot_in_progress = False
        self.selected_player = None
        self.aim_position = None
        if self.ball:
            self.ball.set_velocity(0.0, 0.0)
        for player in self.players:
            player.set_velocity(0.0, 0.0)
        self._update_hud()
        winner_name = locale.TEAM_NAMES.get(winner_team, "")
        self.winner_text.text = locale.WINNER_TEXT.format(team=winner_name)

    def _restart_game(self):
        self.scores = {"blue": 0, "red": 0}
        self.game_over = False
        self.winner_team = None
        self.turn_index = 0
        self.current_team = self.teams[self.turn_index]
        self.winner_text.text = ""
        self.time = 0
        self.time_text.text = "Время: 0"
        self._reset_round(self.current_team)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self._start_music()
        self._update_hud()
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
        if self.goal_timer > 0:
            self.goal_timer = max(0.0, self.goal_timer - delta_time)

        if self.paused or self.game_over:
            self._update_hud()
            return

        self.time += delta_time
        self.time_text.text = f"Время: {int(self.time)}"

        if not self._anything_moving() and not self.shot_in_progress:
            self._update_hud()
            return

        max_speed = 0.0
        if self.ball:
            max_speed = max(max_speed, self.ball.speed())
        for player in self.players:
            max_speed = max(max_speed, player.speed())
        steps = 1
        if max_speed > 0:
            steps = int(math.ceil((max_speed * delta_time) / self.max_move_per_step))
            steps = max(1, min(self.max_substeps, steps))
        step_dt = delta_time / steps

        for _ in range(steps):
            if self.ball:
                self.ball.update(step_dt, self.field.bounds)
            for player in self.players:
                player.update(step_dt, self.field.bounds)
            self._apply_player_player_collisions()
            for player in self.players:
                self._apply_player_ball_collision(player)
            if self._check_goal():
                break
            if self.shot_in_progress and not self._anything_moving():
                self._advance_turn()
                break

        self._update_hud()

    def on_draw(self):
        self.clear()

        self.field.draw()
        for player in self.players:
            player.draw()
        if self.selected_player and not self.paused and not self.game_over:
            arcade.draw_circle_outline(
                self.selected_player.center_x,
                self.selected_player.center_y,
                self.selected_player.radius + 4,
                arcade.color.YELLOW,
                3
            )
            if self.aim_position and not self.shot_in_progress:
                arcade.draw_line(
                    self.selected_player.center_x,
                    self.selected_player.center_y,
                    self.aim_position[0],
                    self.aim_position[1],
                    arcade.color.YELLOW,
                    2
                )
        if self.ball:
            self.ball.draw()

        self.time_text.draw()
        self.turn_text.draw()
        self.status_text.draw()
        self.score_text.draw()

        if self.goal_timer > 0:
            self.goal_text.draw()
        if self.game_over:
            self.winner_text.draw()
            self.restart_text.draw()

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 180)
            )
            self.pause_menu.manager.draw()

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.R:
                self._restart_game()
            return
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            if self.paused:
                self.pause_menu.manager.enable()
            else:
                self.pause_menu.manager.disable()
            self._update_hud()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.paused or self.shot_in_progress or self.game_over:
            return

        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.selected_player = None
            self.aim_position = None
            self._update_hud()
            return

        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        player = self._player_at(x, y, team=self.current_team)
        if player is not None:
            self.selected_player = player
            self.aim_position = (x, y)
            self._update_hud()
            return

        if self.selected_player is not None:
            if self._start_shot(self.selected_player, x, y):
                self.selected_player = None
                self.aim_position = None
                self._update_hud()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.paused or self.shot_in_progress or self.game_over:
            return
        if self.selected_player is not None:
            self.aim_position = (x, y)

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
