import curses
from logging import Logger
from UI.ui import ScreenHandler,Item,GlobalFocusManager


class ReusableActions():


    def __init__(self,screenhandler:"ScreenHandler",logger:Logger) -> None:
        self.screenhandler = screenhandler 
        self.logger = logger
        pass


    @staticmethod
    def changeColor(btn: "Item", cols: list | None = None):
        if cols is None:
            cols = [4, 5]
        x = -1  # fresh x per changeColor(btn) call ✓

        def inner():
            nonlocal x
            # curses.curs_set(0)
            win = btn.win
            x = (x + 1) % len(cols)
            win.bkgd(" ", curses.color_pair(cols[x]))
            win.refresh()
            btn.background = cols[x]
            # logger.info(f"Changing btn color {cols[x]}")
        return inner


    @staticmethod
    def changeColor2(btn: "Item", color: int ):
        def inner():
            win = btn.win
            win.bkgd(" ", curses.color_pair(color))
            win.refresh()
        return inner

    @staticmethod
    def changeColor3(btn: "Item", colors: list[int] ):
        index = -1
        def inner():
            nonlocal index
            win = btn.win

            index += 1
            if index >= len(colors):
                index = 0
            color = colors[index]
            win.bkgd(" ", curses.color_pair(color))
            win.refresh()
        return inner


    def changeScreen(self,screen_identifier:str):
        def inner():
            self.logger.info("Changing screen?")
            GlobalFocusManager.set_spotlight_byid(screen_identifier)
        return inner
