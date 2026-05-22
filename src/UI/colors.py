import curses
import logging
from UI.utils import CustomAdapter,root_logger_name,initialize_root_logger

root = logging.getLogger(root_logger_name)
logger = CustomAdapter(root)

class DefaultColors:
    WIDGET_NORMAL = 1
    WIDGET_FOCUSED = 2


    LAYOUT_NORMAL = 100
    LAYOUT_FOCUSED = 101

    @staticmethod
    def init() -> None:
        logger.info(f"Init default colors {curses.has_colors()}")
        if not curses.has_colors():
            return
        d = DefaultColors
        curses.init_pair(d.WIDGET_NORMAL,curses.COLOR_WHITE,-1)
        curses.init_pair(d.WIDGET_FOCUSED,curses.COLOR_YELLOW,-1)
        curses.init_pair(3,curses.COLOR_GREEN,-1)


        curses.init_pair(d.LAYOUT_NORMAL,curses.COLOR_WHITE,-1)
        curses.init_pair(d.LAYOUT_FOCUSED,curses.COLOR_GREEN,-1)
