import arcade
from view.menu import MenuView
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


def main():
    window = arcade.Window(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE
    )
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()

