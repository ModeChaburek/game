import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIFlatButton, UILabel, UIManager, UISlider
import settings


class Setting_Menu_View(arcade.View):
    def __init__(self, return_view=None):
        super().__init__()

        self.manager = UIManager()

        self.anchor = UIAnchorLayout()
        self.box = UIBoxLayout(vertical=True, space_between=12)

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
        self.back_button = UIFlatButton(text="В меню", width=200)

        @self.volume_slider.event("on_change")
        def _on_volume_change(event):
            self._apply_volume()

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
        self.box.add(self.back_button)

        self.anchor.add(self.box, anchor_x="center", anchor_y="center")
        self.manager.add(self.anchor)

    def _volume_text(self, volume_value):
        return f"Громкость: {int(volume_value * 100)}%"

    def _apply_volume(self):
        new_value = self.volume_slider.value / 100
        self.volume_label.text = self._volume_text(new_value)
        settings.SOUND_VOLUME = new_value
        if settings.MUSIC_PLAYER is not None:
            settings.MUSIC_PLAYER.volume = new_value

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
