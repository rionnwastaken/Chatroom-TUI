import curses
import logging
import math
import _thread
import time
import curses.textpad
import curses.panel
import time
from typing import Callable

logger = logging.getLogger()
logging.basicConfig(filename='window.log', level=logging.INFO)

with open("./window.log","w") as f:
    f.write("")





class Padding():
    def __init__(self, top = 0, right = 0, bottom = 0, left = 0):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def get_padding_horizontal_points(self):
        return self.right + self.left

    def get_padding_vertical_points(self):

        return self.top + self.bottom

class Margin():
    def __init__(self, top = 0, right = 0, bottom = 0, left = 0):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def get_margin_horizontal_points(self):
        return self.right + self.left

    def get_margin_vertical_points(self):
        return self.bottom + self.top





class Item():

    def __init__(self, text = None, margin = Margin(), padding = Padding()):
        self.text = text
        self.length = len(text) if text != None else None 

        self.key:int | None = None
        self.margin:Margin  = margin
        self.padding:Padding  = padding

        self.action = None


        self.win: curses.window | None = None



    def setAction(self,key:int,action:Callable):
        self.action = action
        self.key = key


    def setText(self,text):
        self.text = text
        self.length = len(text)

    def setmargin(self,pad):
        self.margin = pad

    def setWin(self,win:curses.window):
        self.win = win


    def onAction(self):
        if self.action != None:
            self.action()



    def getOccupiedSpace(self,axis:str):

        width_total = 0
        height_total = 0


        if self.length != None:
            width_total += self.length



        width_total += self.margin.right + self.margin.left
        height_total += self.margin.top + self.margin.bottom

        width_total += self.padding.right + self.padding.left
        height_total += self.padding.top + self.padding.bottom


        #logging
        if self.length == None:
            logger.error("Item has no length")

        return (height_total,width_total)

        # if axis == "vertical":
        #     pass

    def getInnerSpace(self):
        if self.length != None:
            return self.length

        logger.error("Item has no length")
        return 0 



    def getmargin(self):
        return self.margin


        


    def getText(self):

        if self.text != None:
            return self.text

        logger.error("Text in item is None")
        return ""

    def getKey(self):
        return self.key 




class Menu():

    def __init__(self,topx=None,topy=None,axis="horizontal",min_height=None,min_width=None) -> None:
        self.items:list["Item"] = []
        self.rendered = False
        self.menu_win:curses.window | None = None

        self.total_width = 0
        self.total_height = 0

        self.topx = topx
        self.topy = topy
        self.axis = axis
        self.min_height = None
        self.min_width = None


        self.default_border_horizontal_padding = 2
        self.default_border_vertical_padding = 2
        self.default_label_height = 3
        pass


    def addItem(self,item:"Item"):
        self.items.append(item)


    def show(self,v):
        if not self.rendered and v == True:
            self._render()
            self.rendered = True


    def _create_menu_window(self):

        height_total = 0
        width_total = 0
        max_height = 0
        max_width = 0
        for item in self.items:
            item_heigth_total,item_width_total = item.getOccupiedSpace(self.axis)
            item_width_total += self.default_border_horizontal_padding
            item_heigth_total += self.default_label_height

            width_total += item_width_total
            height_total += item_heigth_total

            if item_width_total > max_width:
                max_width = item_width_total

            if item_heigth_total > max_height:
                max_height = item_heigth_total



        if self.axis == 'horizontal':
            self.total_width += width_total 
            logger.info(f"max height {max_height}")
            self.total_height += max_height

        elif self.axis == 'vertical':
            self.total_width += max_width
            logger.info(f"max height {height_total}")
            self.total_height += height_total
            pass

        
        # if self.min_width != None and self.total_width < self.min_width:
        #     self.total_width = self.min_width
        #
        # if self.min_height != None and self.total_height < self.min_height:
        #     self.total_height = self.min_height


        if (self.topy == None or self.topx == None):
            logger.info(f"Coordinate None topx {self.topx} topy {self.topy}")
            return

        self.menu_win = curses.newwin(self.total_height,self.total_width,self.topy,self.topx)
        self.menu_win.bkgd(" ",curses.color_pair(1))


    def _render(self):
        # self.menu_win.box()
        # self.menu_win.bkgd(" ",curses.color_pair(1))

        self._create_menu_window()
        if self.menu_win == None:
            return

        current_posx = 0
        current_posy = 0
        #Create subwins
        for item in self.items:
            width_total = item.getInnerSpace()
            margin = item.margin
            padding = item.padding

            #Dont include margin, margin affects the posy
            win_lines = sum([
                1,
                self.default_border_vertical_padding,
                padding.get_padding_vertical_points(),
                ])

            #Dont include margin, margin affects the posx
            win_cols = sum([
                    width_total,
                    self.default_border_horizontal_padding,
                    padding.get_padding_horizontal_points(),
                ])

                

            logger.info(f"menuwin {self.menu_win.getmaxyx()}")
            logger.info(f"itemwin {win_lines, win_cols, current_posy, current_posx}")

            item_win:curses.window = self.menu_win.derwin(
                win_lines,
                win_cols,
                current_posy,
                current_posx
            )

            text_posy = 1 + item.padding.top
            text_posx = 1 + item.padding.left
            
            item_win.addstr(text_posy,text_posx,item.getText())
            item_win.box()
            item_win.refresh()
            item.setWin(item_win)

        
            if self.axis == 'horizontal':
            
                current_posx += sum([
                    width_total,
                    margin.get_margin_horizontal_points(),
                    padding.get_padding_horizontal_points(),
                    self.default_border_horizontal_padding,
                    
                ]) 

            if self.axis == 'vertical':
                current_posy  += sum([
                    item_win.getmaxyx()[0],        
                    margin.bottom,
                    # padding.bottom
                    ])


        self.menu_win.refresh()


            


    def handleKey(self,key):
        for item in self.items:
            if (key == item.getKey()):
                item.onAction()

    










class Main():

    def __init__(self) -> None:

        curses.wrapper(self.main)

    def create_window(self,y,x,h,w) -> curses.window:
        win = curses.newwin(h, w, y, x)
        return win


    def init_colors(self):

        if curses.has_colors():
            curses.start_color()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)


        logger.info(f"COlors are : ?{ curses.COLOR_WHITE,curses.COLOR_BLUE }")




    def main(self,stdsrc:curses.window):
        self.init_colors()



        stdsrc.timeout(100)
        stdsrc.refresh()
        curses.use_default_colors()

        
        menu = Menu(topx=10,topy=5,axis="horizontal")
        login_item = Item(text="Log in (1)",margin=Margin(0,1,0,0),padding=Padding(2,2,2,2))
        signup_item = Item(text="Sign up (2)",margin=Margin(0,1,0,0))
        shit = Item(text="whatup",margin=Margin(0,0,0,0))

        # shit = Item(text="Shit",margin=Margin(0,10,0,0),padding=Padding(2,2,2,2))


        menu.addItem(login_item)
        menu.addItem(signup_item)
        menu.addItem(shit)

        
        menu.show(True)


        curses.mousemask(curses.BUTTON1_CLICKED)
        curses.mouseinterval(0)

        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue

            pass


Main()




