import curses
import logging
from typing import Callable
from UI.utils import CustomAdapter,root_logger_name,initialize_root_logger
import math
from abc import ABC

root = logging.getLogger(root_logger_name)
logger = CustomAdapter(root)


color_id_count = 10
pair_id_count = 10

class Color:




    def __init__(self,initial_id) -> None:
        self.initial_id = initial_id
        logger.info("FUCK FUCK SHIT")

    def __mul__(self,other):


        if not isinstance(other,int):
            raise Exception(f"Must use an integer. Wrong type {type(other)}")

        if other > ColorCreator.LevelLimit:
            raise Exception(f"Cant use level greater than {ColorCreator.LevelLimit}")

        id_color = self.initial_id + other -1
        logger.debug(f"Initial id {self.initial_id} and new id color {id_color} and offset {other}, real {other -1}")
        return curses.color_pair(id_color)

    def initial(self):
        return curses.color_pair(self.initial_id)


#TODO allow creation of layers parent child colors, dont affect each other
class ColorCreator(ABC):
    LevelLimit = 5
    def __init__(self) -> None:
        super().__init__()




    def convert_color(self,r,g,b):
        
        def convert(v:int):
            if v > 255:
                raise Exception(f"Not valid rgb value: {v}")
            logger.info(f"COlor is {math.ceil( v / 255 * 1000)}")

            return math.ceil( v / 255 * 1000)

        r,g,b = convert(r),convert(g),convert(b)
        logger.info(f"Here have {r,g,b}")
        return r,g,b

    def color(self,r,g,b):
        global color_id_count
        color_id_count += 1
        logger.info(f"Color id count is {color_id_count}")
        curses.init_color(color_id_count,*self.convert_color(r,g,b))
        return color_id_count

    def pair(self,fg,bg) -> Color:
        global pair_id_count


        initial_id = pair_id_count
        color =  Color(initial_id)

        for offset in range(0,ColorCreator.LevelLimit):
            id = initial_id + offset
            curses.init_pair(id,fg,bg)
            logger.debug(f"Creating pair id,fg,bg {id} {fg} {bg}")

        pair_id_count += ColorCreator.LevelLimit

        return color







class DefaultColors(ColorCreator):


    instance = None

    def __init__(self) -> None:
        pass
        


    def init_colors(self):
        # self.WIDGET_NORMAL = self.pair(curses.COLOR_WHITE,-1)
        self.NORMAL_FOCUSED_YELLOW =  self.pair(curses.COLOR_YELLOW,-1)
        self.NORMAL = self.pair(curses.COLOR_WHITE,-1)
        self.NORMAL_PURPLE = self.pair(curses.COLOR_MAGENTA,-1)
        self.NORMAL_GREEN = self.pair(curses.COLOR_GREEN,-1)

        self.NORMAL_FOCUSED_BLUE = self.pair(curses.COLOR_BLUE,-1)

        self.PURPLE = self.pair(curses.COLOR_WHITE,curses.COLOR_MAGENTA)




    @staticmethod
    def get_instance():
        if DefaultColors.instance == None:
            DefaultColors.instance = DefaultColors()

        return DefaultColors.instance



