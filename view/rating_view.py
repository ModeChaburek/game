import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIFlatButton, UILabel, UIManager
import db


class RatingView(arcade.View):

    def __init__(self, return_view=None):
        super().__init__()

        self.manager = UIManager()

        anchor = UIAnchorLayout()
        box = UIBoxLayout(vertical=True, space_between=10)

        title_label = UILabel(
            text="Рейтинг",
            font_size=40,
            text_color=arcade.color.WHITE
        )
        box.add(title_label)

        header = UIBoxLayout(vertical=False, space_between=60)
        header.add(UILabel(text="Игрок 1", font_size=18, text_color=arcade.color.YELLOW))
        header.add(UILabel(text="Игрок 2", font_size=18, text_color=arcade.color.YELLOW))
        header.add(UILabel(text="Счет", font_size=18, text_color=arcade.color.YELLOW))
        box.add(header)

        self._add_results(box)

        back_button = UIFlatButton(text="В меню", width=200)

        @back_button.event("on_click")
        def _on_back_click(event):
            if return_view is None:
                from view.menu import MenuView
                self.window.show_view(MenuView())
            else:
                self.window.show_view(return_view)

        box.add(back_button)

        anchor.add(box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def _add_results(self, box):
        try:
            results = db.get_latest_results(limit=10)
        except Exception:
            box.add(UILabel(text="Ошибка загрузки рейтинга", font_size=18, text_color=arcade.color.RED))
            return

        if not results:
            box.add(UILabel(text="Пока нет результатов", font_size=18, text_color=arcade.color.WHITE))
            return

        for row in results:
            row_box = UIBoxLayout(vertical=False, space_between=60)
            row_box.add(UILabel(text=str(row["player1"]), font_size=16, text_color=arcade.color.WHITE))
            row_box.add(UILabel(text=str(row["player2"]), font_size=16, text_color=arcade.color.WHITE))
            row_box.add(UILabel(text=f"{row['score1']} : {row['score2']}", font_size=16, text_color=arcade.color.WHITE))
            box.add(row_box)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
