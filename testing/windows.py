from ast import Tuple
import curses
import logging
import math
import _thread
import time
import curses.textpad
import curses.panel
import time
from typing import Callable,Literal,TypedDict
from abc import ABC, abstractmethod

logger = logging.getLogger()
logging.basicConfig(filename='window.log', level=logging.INFO)

with open("./window.log","w") as f:
    f.write("")



'''
Spotlight is the current screen that receives the input
'''

class Coordinates(TypedDict):
    topx:int
    topy:int

class ScreenHandler():
    def __init__(self) -> None:
        self.spotlight:Menu | None = None
        self.screens:dict[str,Menu] = {}


    def add_screen(self,screen_name_identifier,screen):
        if self.screens.get(screen_name_identifier) != None:
            logger.info(f"{screen_name_identifier} cannot be added twice")
            return

        self.screens[screen_name_identifier] = screen

    def removeLight(self):
        self.spotlight = None

    def set_spotlight(self,screen_name_identifier):

        screen:Menu | None = self.screens.get(screen_name_identifier)
        if screen == None:
            logger.info(f"'{screen_name_identifier}' screen was not found")
            return
        self.spotlight = screen
        self.spotlight.show(True)

    def handleKey(self,c):
        if self.spotlight != None:
            self.spotlight.handleKey(c)





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

'''
Glossary
Focusable: means that it can receive focus and be the only thing that can receive input at the moment
Global focus: When there are no focused items, global key listening is present (good for menus?)
'''



'''
A screen creates a window that uses the whole screen and is responsible for holding layouts
Screen determines which layout has focus
The focused layout receives the keystroke
The focused has a  bidirection traversal
There is no global_keys for the screen, at least one layout forcefully needs spotlight but layouts dont need to be focusable necesarilly
'''
class Screen():

    def __init__(self,screen_name_identifier) -> None:
        self.layouts:list["Layout"] = []
        self.spotlight:None | Layout = None
        self.traversal_index = 0
        self.screen_name_identifier = screen_name_identifier

    
    def add_layout(self,layout:"Layout"):
        self.layouts.append(layout)



    def set_spotlight(self,layout:"Layout"):
        self.spotlight = layout
        self.traversal_index = -1
        for index,lay in enumerate( self.layouts ):
            if self.spotlight == lay:
                self.traversal_index = index

        if self.traversal_index == -1:
            raise Exception(f"Screen [{self.screen_name_identifier}]  func [set_spotlight] traversal_index was not found")


    def traverse(self,direction:Literal["forward","backward"]):
        magnitude = 1 if direction == "forward" else -1


        count = 0
        while (True):
            self.traversal_index += magnitude

            if self.traversal_index < 0:
                self.traversal_index = len(self.layouts) - 1

            if self.traversal_index >= len(self.layouts):
                self.traversal_index = 0 

            next_layout = self.layouts[self.traversal_index]
            if next_layout.focusable:
                self.spotlight = next_layout
                break

            count += 0
            if count >= len(self.layouts) + 5:
                raise Exception("class Screen func [traverse] There is error in travesal infinite while loop")

        # if (self.traversal)




    def handleKey(self,c):
        if self.spotlight != None:
            self.spotlight.handleKey(c)
            return

        raise Exception(f"class [Screen] func [handleKey] spotlight is None")




''' 
A layout is a window that holds items
It calculates the  required dimensions to fit the items
It controls which item receives the keystroke
A layout can only one type focusable or have global keys


Layout creates the derevied windows for the Items

'''
class Layout():
    def __init__(self,coordinates:Coordinates,focusable=True, axis:Literal["horizontal","vertical"] = "horizontal",global_keys = False) -> None:
        self.focusable = focusable
        self.items:list["Otom"] = []
        self.axis = axis
        self.traversal_index = 0
        self.layout_window:curses.window

        #Length,margins,padding everything
        self.total_width = 0 
        self.total_height = 0

        self.topx = coordinates["topx"]
        self.topy = coordinates["topy"]
        self.axis = axis
        self.min_height = None
        self.min_width = None

        self.default_border_padding = 2



        self.there_are_global_keys = global_keys

        self.spotlight:Otom | None = None

    class LayoutRenderer():
        def __init__(self,l:"Layout") -> None:
            self.l = l
            pass

        def _create_menu_window(self):

            height_total = 0
            width_total = 0
            max_height = 0
            max_width = 0
            for item in self.l.items:
                item_heigth_total,item_width_total = item.getOccupiedSpace(self.l.axis)
                item_width_total += self.l.default_border_horizontal_padding
                item_heigth_total += self.l.default_label_height

                width_total += item_width_total
                height_total += item_heigth_total

                if item_width_total > max_width:
                    max_width = item_width_total

                if item_heigth_total > max_height:
                    max_height = item_heigth_total



            if self.l.axis == 'horizontal':
                self.l.total_width += width_total 
                logger.info(f"max height {max_height}")
                self.l.total_height += max_height

            elif self.l.axis == 'vertical':
                self.l.total_width += max_width
                logger.info(f"max height {height_total}")
                self.l.total_height += height_total
                pass

            
            # if self.l.min_width != None and l.total_width < l.min_width:
            #     self.l.total_width = l.min_width
            #
            # if self.l.min_height != None and l.total_height < l.min_height:
            #     self.l.total_height = l.min_height


            if (self.l.topy == None or l.topx == None):
                logger.info(f"Coordinate None topx {self.l.topx} topy {l.topy}")
                return

            self.l.menu_win = curses.newwin(l.total_height,l.total_width,l.topy,l.topx)
            # self.l.menu_win.bkgd(" ",curses.color_pair(1))


        def _render(self):
            # self.menu_win.box()
            # self.l.menu_win.bkgd(" ",curses.color_pair(1))

            self._create_menu_window()
            if self.l.menu_win == None:
                return

            current_posx = 0
            current_posy = 0
            #Create subwins
            for item in self.l.items:
                width_total = item.getInnerSpace()
                margin = item.margin
                padding = item.padding

                #Dont include margin, margin affects the posy
                win_lines = sum([
                    1,
                    self.l.default_border_vertical_padding,
                    padding.get_padding_vertical_points(),
                    ])

                #Dont include margin, margin affects the posx
                win_cols = sum([
                        width_total,
                        self.l.default_border_horizontal_padding,
                        padding.get_padding_horizontal_points(),
                    ])

                    

                logger.info(f"menuwin {self.l.menu_win.getmaxyx()}")
                logger.info(f"itemwin {win_lines, win_cols, current_posy, current_posx}")

                item_win:curses.window = self.l.menu_win.derwin(
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

            
                if self.l.axis == 'horizontal':
                
                    current_posx += sum([
                        width_total,
                        margin.get_margin_horizontal_points(),
                        padding.get_padding_horizontal_points(),
                        self.l.default_border_horizontal_padding,
                        
                    ]) 

                if self.l.axis == 'vertical':
                    current_posy  += sum([
                        item_win.getmaxyx()[0],        
                        margin.bottom,
                        # padding.bottom
                        ])


            self.l.menu_win.refresh()

        


    def add_item(self,item:"Otom"):
        if self.there_are_global_keys and item.focusable:
            raise Exception("class [Layout] func [add_item] cannot add item that is focusable when there are global keys")

        self.items.append(item)


    def set_spotlight(self,item:"Otom"):
        if self.there_are_global_keys == True:
            raise Exception("class [Layout] func [set_spotlight] cannot set spotlight when there are global keys")

        self.spotlight = item
        self.traversal_index = -1
        for index,item in enumerate( self.items ):
            if self.spotlight == item:
                self.traversal_index = index

        if self.traversal_index == -1:
            raise Exception(f"class [Layout]  func [set_spotlight] item was not found in items")


    def traverse(self,direction:Literal["forward","backward"]):

        if self.there_are_global_keys:
            raise Exception(f"class [Layout]  func [traverse] cannot traverse when there are global keys")


        magnitude = 1 if direction == "forward" else -1
        count = 0

        while (True):
            self.traversal_index += magnitude

            if self.traversal_index < 0:
                self.traversal_index = len(self.items) - 1

            if self.traversal_index >= len(self.items):
                self.traversal_index = 0 

            next_layout = self.items[self.traversal_index]
            if next_layout.focusable:
                self.spotlight = next_layout
                break

            count += 0
            if count >= len(self.items) + 5:
                raise Exception("class Screen func [traverse] There is error in travesal infinite while loop")


    def hide(self):
        self.layout_window.clear()
        self.layout_window.refresh()


    def handleKey(self,c):

        if self.there_are_global_keys:
            for item in self.items:
                global_key = item.global_key
                if c == global_key:
                    item.onAction()
        else:
            if self.spotlight == None:
                raise Exception("class [Layout] func [handleKey] cannot handle key when spotlight is None")

            self.spotlight.handleKey(c)

        pass


'''
Item can hold anything, it only cares about its dimensions 
Item is widget holder for example for labels ,inputs
Item cannot be focusable and have global_key at the same time
When a layout is of type global, all of its items must be of type global_key
'''
class Otom(ABC):

    def __init__(self,lines:int,cols:int,focusable = False,global_key:int = -1,margin = Margin(),padding = Padding(),hasBorder=False) -> None:

        if focusable and global_key != -1:
            raise Exception("class [Otom] func [__init__] item cannot be focusable and have global_key at the same time")

        self.focusable = focusable
        self.global_key = global_key
        self.has_border = hasBorder

        self.lines = lines
        self.cols = cols

        self.margin = margin
        self.padding = padding

        self.win:curses.window
        pass

    def set_win(self,win:curses.window):
        self.win = win

    def get_total_space(self):
        lines = self.lines + self.margin.bottom + self.margin.top +  self.padding.top + self.padding.bottom
        cols = self.cols + self.margin.right + self.margin.left + self.padding.right + self.padding.left

        return (lines,cols)


    @abstractmethod
    def renderItem(self,window:curses.window):
        raise NotImplementedError()


    @abstractmethod
    def handleKey(self,c):
        raise NotImplementedError()

    def onAction(self):
        return None
    



'''Here lines and cols dont take into considerations the space of the window borders '''
class Label(Otom):
    def __init__(self,text,margin=Margin(), padding=Padding(),hasBorder=False) -> None:
        self.length = len(text)
        self.text = text
        super().__init__(1,self.length, margin=margin, padding=padding,hasBorder=hasBorder)


    def rederItem(self,window:curses.window):
        if not self.has_border:
            window.addstr(0,0,self.text)

        else:
            window.addstr(1,1,self.text)








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
        self.menu_win:curses.window 

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

    def hide(self):
        self.menu_win.clear()
        self.menu_win.refresh()




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
        # self.menu_win.bkgd(" ",curses.color_pair(1))


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
        curses.mousemask(curses.BUTTON1_CLICKED)
        curses.mouseinterval(0)

        stdsrc.refresh()
        curses.use_default_colors()


        menu2 = Menu(topx=10,topy=20)
        manzana = Item(text="whatup?")
        menu2.addItem(manzana)


        menuHandler = ScreenHandler()

        
        menu = Menu(topx=10,topy=5,axis="horizontal")
        login_item = Item(text="Log in (1)",margin=Margin(0,1,0,0),padding=Padding(2,2,2,2))
        signup_item = Item(text="Sign up (2)",margin=Margin(0,1,0,0))
        shit = Item(text="whatup",margin=Margin(0,0,0,0))
        dogs = Item(text="Who let the dogs out?")

        def login_action():
            menu.hide()
            menuHandler.removeLight()
            menuHandler.set_spotlight("menu2")
            


            # stdsrc.refresh()
        login_item.setAction(ord("1"),login_action)
        menu.addItem(login_item)
        menu.addItem(signup_item)
        menu.addItem(shit)
        menu.addItem(dogs)




        menuHandler.add_screen("menu",menu)
        menuHandler.add_screen("menu2",menu2)
        menuHandler.set_spotlight("menu")



        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue

            menuHandler.handleKey(c)
            pass


Main()




