from typing import Callable
from UI.attributes import DefaultAttrbutes, DefaultAttributeManager
from UI.colors import DefaultColors
from UI.properties import Padding, Push
from UI.utils import initialize_root_logger
import curses
from UI.ui import GlobalKeyLayout, Label, ScreenHandler,Item,Layout
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


def init_default_attributes():

    defaultcolors = DefaultColors.get_instance()
    DefaultAttributeManager.init_default_attrs(Item,DefaultAttrbutes(

                    push=Push(),
                    padding=Padding(),
                    background=defaultcolors.NORMAL_PURPLE * Item.color_level,
                    background_focus=defaultcolors.NORMAL_FOCUSED_YELLOW * Item.color_level,
                    hasBorder=True

        ))


    DefaultAttributeManager.init_default_attrs(Layout,DefaultAttrbutes(

                    push=Push(),
                    padding=Padding(),
                    background=defaultcolors.NORMAL * Layout.color_level,
                    background_focus=defaultcolors.NORMAL_FOCUSED_BLUE * Layout.color_level,
                    hasBorder=True

        ))


    DefaultAttributeManager.init_default_attrs(Label,DefaultAttrbutes(
                    hasBorder=False
        ))


    DefaultAttributeManager.init_default_attrs(GlobalKeyLayout,DefaultAttrbutes(
                    background=defaultcolors.NORMAL_GREEN * Layout.color_level
        ))





def event_loop(init_func:Callable):

    def main(stdsrc):

        stdsrc.timeout(100)
        curses.curs_set(0)
        stdsrc.refresh()

        screenHandler =   ScreenHandler.init_screenHandler(stdsrc)

        init_colors()
        init_default_attributes()
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




