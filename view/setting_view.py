import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIFlatButton, UILabel, UIManager, UISlider
import settings


class Setting_Menu_View(arcade.View):
    def __init__(self, return_view=None):
        super().__init__()

        self.manager = UIManager()

        self.anchor = UIAnchorLayout()
        self.box = UIBoxLayout(vertical=True, space_between=12)

        self._normalize_color_indexes()

        self.title_label = UILabel(
            text="Настройки",
            font_size=40,
            text_color=arcade.color.WHITE
        )
        self.volume_label = UILabel(
            text=self._volume_text(settings.SOUND_VOLUME),
            font_size=18,
            text_color=arcade.color.WHITE
        )
        self.volume_slider = UISlider(
            value=int(settings.SOUND_VOLUME * 100),
            min_value=0,
            max_value=100,
            width=300
        )
        self.blue_color_label = UILabel(
            text=self._color_text("синих", settings.TEAM_BLUE_COLOR_INDEX),
            font_size=18,
            text_color=self._color_value(settings.TEAM_BLUE_COLOR_INDEX)
        )
        self.blue_color_button = UIFlatButton(text="Сменить цвет", width=220)
        self.red_color_label = UILabel(
            text=self._color_text("красных", settings.TEAM_RED_COLOR_INDEX),
            font_size=18,
            text_color=self._color_value(settings.TEAM_RED_COLOR_INDEX)
        )
        self.red_color_button = UIFlatButton(text="Сменить цвет", width=220)
        self.back_button = UIFlatButton(text="В меню", width=200)

        @self.volume_slider.event("on_change")
        def _on_volume_change(event):
            self._apply_volume()

        @self.blue_color_button.event("on_click")
        def _on_blue_color_click(event):
            settings.TEAM_BLUE_COLOR_INDEX = self._next_color_index(
                settings.TEAM_BLUE_COLOR_INDEX,
                settings.TEAM_RED_COLOR_INDEX
            )
            self._refresh_color_labels()

        @self.red_color_button.event("on_click")
        def _on_red_color_click(event):
            settings.TEAM_RED_COLOR_INDEX = self._next_color_index(
                settings.TEAM_RED_COLOR_INDEX,
                settings.TEAM_BLUE_COLOR_INDEX
            )
            self._refresh_color_labels()

        @self.back_button.event("on_click")
        def _on_back_click(event):
            if return_view is None:
                from view.menu import MenuView
                self.window.show_view(MenuView())
            else:
                self.window.show_view(return_view)

        self.box.add(self.title_label)
        self.box.add(self.volume_label)
        self.box.add(self.volume_slider)
        self.box.add(self.blue_color_label)
        self.box.add(self.blue_color_button)
        self.box.add(self.red_color_label)
        self.box.add(self.red_color_button)
        self.box.add(self.back_button)

        self.anchor.add(self.box, anchor_x="center", anchor_y="center")
        self.manager.add(self.anchor)

    def _volume_text(self, volume_value):
        return f"Громкость: {int(volume_value * 100)}%"

    def _color_text(self, team_label, color_index):
        return f"Цвет {team_label}: {self._color_name(color_index)}"

    def _color_name(self, color_index):
        options = settings.TEAM_COLOR_OPTIONS
        if not options:
            return "нет"
        return options[color_index % len(options)][0]

    def _color_value(self, color_index):
        options = settings.TEAM_COLOR_OPTIONS
        if not options:
            return arcade.color.WHITE
        return options[color_index % len(options)][1]

    def _normalize_color_indexes(self):
        options = settings.TEAM_COLOR_OPTIONS
        if not options:
            return
        settings.TEAM_BLUE_COLOR_INDEX %= len(options)
        settings.TEAM_RED_COLOR_INDEX %= len(options)
        if len(options) > 1 and settings.TEAM_BLUE_COLOR_INDEX == settings.TEAM_RED_COLOR_INDEX:
            settings.TEAM_RED_COLOR_INDEX = (settings.TEAM_RED_COLOR_INDEX + 1) % len(options)

    def _next_color_index(self, current_index, locked_index):
        options = settings.TEAM_COLOR_OPTIONS
        if not options or len(options) == 1:
            return current_index
        index = current_index
        for _ in range(len(options)):
            index = (index + 1) % len(options)
            if index != locked_index:
                return index
        return current_index

    def _refresh_color_labels(self):
        self._normalize_color_indexes()
        self.blue_color_label.text = self._color_text(
            "синих",
            settings.TEAM_BLUE_COLOR_INDEX
        )
        self.blue_color_label.text_color = self._color_value(
            settings.TEAM_BLUE_COLOR_INDEX
        )
        self.red_color_label.text = self._color_text(
            "красных",
            settings.TEAM_RED_COLOR_INDEX
        )
        self.red_color_label.text_color = self._color_value(
            settings.TEAM_RED_COLOR_INDEX
        )

    def _apply_volume(self):
        new_value = self.volume_slider.value / 100
        self.volume_label.text = self._volume_text(new_value)
        settings.SOUND_VOLUME = new_value
        if settings.MUSIC_PLAYER is not None:
            settings.MUSIC_PLAYER.volume = new_value

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self._refresh_color_labels()
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
