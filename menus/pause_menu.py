from arcade.gui import *

class PauseMenu:
    def __init__(self, on_continue, on_menu, on_settings):
        self.manager = UIManager()

        anchor = UIAnchorLayout()
        box = UIBoxLayout(vertical=True, space_between=10)

        btn_continue = UIFlatButton(text="Продолжить", width=200)
        btn_menu = UIFlatButton(text="В меню", width=200)
        btn_settings = UIFlatButton(text="Настройки", width=200)

        @btn_continue.event("on_click")
        def _(event):
            on_continue()

        @btn_menu.event("on_click")
        def _(event):
            on_menu()

        @btn_settings.event("on_click")
        def _(event):
            on_settings()

        box.add(btn_continue)
        box.add(btn_menu)
        box.add(btn_settings)

        anchor.add(box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)
