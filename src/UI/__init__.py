from typing import Callable
from UI.colors import DefaultColors
from UI.utils import initialize_root_logger
import curses
from UI.ui import ScreenHandler
import time 
import logging

initialize_root_logger()


logger = logging.getLogger()

def init_colors():
    if curses.has_colors():
        curses.start_color()

    curses.use_default_colors()

    logger.info(f"Color black {curses.COLOR_BLACK}")
    logger.info(f"Color white {curses.COLOR_WHITE}")

    defaultcolors = DefaultColors.get_instance()
    defaultcolors.init_colors()


def event_loop(init_func:Callable):

    def main(stdsrc):

        stdsrc.timeout(100)
        curses.curs_set(0)
        stdsrc.refresh()

        screenHandler =   ScreenHandler.init_screenHandler(stdsrc)

        init_colors()
        init_func()
        while(1):
            start = time.perf_counter()
            c = stdsrc.getch()
            end = time.perf_counter(
            )


            if c == -1:
                continue

            if c == curses.KEY_RESIZE:
                continue

            screenHandler.handleKey(c)


    curses.wrapper(main)




