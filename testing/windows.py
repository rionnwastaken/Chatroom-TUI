from ast import Tuple
import curses
import logging
import math
import _thread
from os import terminal_size
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
    def __init__(self,terminal_window) -> None:
        Screen.terminal_window = terminal_window
        self.terminal_window = terminal_window
        self.spotlight:Screen | None = None
        self.screens:dict[str,Screen] = {}


    def add_screen(self,screen:"Screen"):
        if self.screens.get(screen.screen_name_identifier) != None:
            logger.info(f"{screen.screen_name_identifier} cannot be added twice")
            return

        self.screens[screen.screen_name_identifier] = screen

    def removeLight(self):
        self.spotlight = None

    def set_spotlight(self,screen_name_identifier):

        screen:Screen | None = self.screens.get(screen_name_identifier)
        if screen == None:
            logger.info(f"'{screen_name_identifier}' screen was not found")
            return
        self.spotlight = screen
        self.spotlight.show()

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

class Push():
    def __init__(self, top = 0, right = 0, bottom = 0, left = 0):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def get_push_horizontal_points(self):
        return self.right + self.left

    def get_push_vertical_points(self):
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

    terminal_window:curses.window

    def __init__(self,screen_name_identifier) -> None:
        term_lines,term_cols = Screen.terminal_window.getmaxyx() 
        self.screen_window = curses.newwin(term_lines,term_cols,0,0)
        self.layouts:list["Layout"] = []
        self.spotlight:None | Layout = None
        self.traversal_index = 0
        self.screen_name_identifier = screen_name_identifier

    
    def add_layout(self,layout:"Layout"):
        layout.screen_window = self.screen_window
        self.layouts.append(layout)


    def show(self):
        for lay in self.layouts:
            lay.show()
        self.screen_window.bkgd(" ",curses.color_pair(1))
        self.screen_window.refresh()
        pass





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
    def __init__(self,coordinates:Coordinates,focusable=True, axis:Literal["horizontal","vertical"] = "horizontal",global_keys = False,padding=Padding(),push=Push()) -> None:
        self.focusable = focusable
        self.items:list["Otom"] = []
        self.axis = axis
        self.traversal_index = 0
        self.layout_window:curses.window

        self.padding = padding
        self.push = push

        #Length,margins,padding everything
        self.total_width = 0 
        self.total_height = 0

        self.topx = coordinates["topx"]
        self.topy = coordinates["topy"]
        self.axis = axis
        self.min_height = None
        self.min_width = None

        self.default_border_padding = 2

        self.screen_window:curses.window



        self.there_are_global_keys = global_keys

        self.spotlight:Otom | None = None


        if (self.topy == None or self.topx == None):
            raise Exception(f"Coordinate None topx {self.topx} topy {self.topy}")


    def _create_menu_window(self):

        layout_height = 0
        layout_width = 0

        biggerst_height = 0
        biggest_width = 0

        for item in self.items:
            item_lines,item_cols = item.get_total_space()

            if item.has_border:
                item_cols += self.default_border_padding
                item_lines += self.default_border_padding

            layout_width += item_cols
            layout_height += item_lines

            if item_cols > biggest_width:
                biggest_width = item_cols

            if item_lines > biggerst_height:
                biggerst_height = item_lines



        #Only has to as tall as the tallest item
        if self.axis == 'horizontal':
            self.total_width += layout_width 
            logger.info(f"max height {biggerst_height}")
            self.total_height += biggerst_height

        #Only has to as wide as the widest item
        elif self.axis == 'vertical':
            self.total_width += biggest_width
            logger.info(f"max height {layout_height}")
            self.total_height += layout_height
            pass


        

        
        # if self.min_width != None and self.total_width < self.min_width:
        #     self.total_width = self.min_width
        #
        # if self.min_height != None and self.total_height < self.min_height:
        #     self.total_height = self.min_height


        # self.total_height += 10
        # self.total_width += 10

        self.layout_window = self.screen_window.derwin(self.total_height,self.total_width,self.topy,self.topx)

        # self.layout_window.box()

        logger.info(f"layout_window size {self.layout_window.getmaxyx()}")
        # self.menu_win.bkgd(" ",curses.color_pair(1))

    def show(self):
        self._render()


    def _render(self):
        # self.menu_win.box()
        # self.menu_win.bkgd(" ",curses.color_pair(1))

        self._create_menu_window()

        if self.layout_window == None:
            raise Exception("Layout window is null")

        current_posx = 0
        current_posy = 0
        #Create subwins
        for item in self.items:
            width = item.cols
            height = item.lines
            margin = item.push
            padding = item.padding

            border = self.default_border_padding if item.has_border else 0

            #Dont include margin, margin affects the posy
            win_lines = sum([
                height,
                border,
                padding.get_padding_vertical_points(),
                ])

            #Dont include margin, margin affects the posx
            win_cols = sum([
                    width,
                    border,
                    padding.get_padding_horizontal_points(),
                ])

                

            logger.info(f"menuwin {self.layout_window.getmaxyx()}")
            logger.info(f"itemwin {win_lines, win_cols, current_posy, current_posx}")

            item_win:curses.window = self.layout_window.derwin(
                win_lines,
                win_cols,
                current_posy,
                current_posx
            )

            item.renderItem(item_win)

        
            if self.axis == 'horizontal':
            
                current_posx += sum([
                    width,
                    margin.get_push_horizontal_points(),
                    padding.get_padding_horizontal_points(),
                    border,
                    
                ]) 

            if self.axis == 'vertical':
                current_posy  += sum([
                    item_win.getmaxyx()[0],        
                    margin.bottom,
                    # padding.bottom
                    ])

        self.layout_window.bkgd(" ",curses.color_pair(2))
        self.layout_window.refresh()

    


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
                #:
                if item.global_key != None:
                    global_key = item.global_key
                    if c == global_key:
                        item.onAction()
        else:
            if self.spotlight != None:
                self.spotlight.handleKey(c)
                # raise Exception("class [Layout] func [handleKey] cannot handle key when spotlight is None")

            

        pass


'''
Item can hold anything, it only cares about its dimensions 
Item is widget holder for example for labels ,inputs
Item cannot be focusable and have global_key at the same time
When a layout is of type global, all of its items must be of type global_key
When focusable is False and global key is None, it means its a static item
'''
class Otom(ABC):

    def __init__(self,lines:int,cols:int,focusable = False,global_key = None,push = Push(),padding = Padding(),hasBorder=False,background=None) -> None:

        if focusable and global_key != -1:
            raise Exception("class [Otom] func [__init__] item cannot be focusable and have global_key at the same time")

        self.focusable = focusable
        self.global_key = global_key
        self.has_border = hasBorder
        self.background = background

        self.lines = lines
        self.cols = cols

        self.push = push
        self.padding = padding

        self.win:curses.window
        pass

    def set_win(self,win:curses.window):
        self.win = win

    def get_total_space(self) -> tuple[int,int]:
        lines = self.lines + self.push.bottom + self.push.top +  self.padding.top + self.padding.bottom
        cols = self.cols + self.push.right + self.push.left + self.padding.right + self.padding.left

        return (lines,cols)


    @abstractmethod
    def renderItem(self,window:curses.window):
        raise NotImplementedError()


    def handleKey(self,c):
        raise NotImplementedError()

    def onAction(self):
        return None
    



'''Here lines and cols dont take into considerations the space of the window borders '''
class Label(Otom):
    def __init__(self,text,push=Push(), padding=Padding(),hasBorder=False,background=None) -> None:
        self.length = len(text)
        self.text = text
        self.win:curses.window
        super().__init__(1,self.length, push=push, padding=padding,hasBorder=hasBorder,background=background)


    def renderItem(self,window:curses.window):
        self.win = window

        if self.background != None:
            self.win.bkgd(" ", curses.color_pair(self.background))

        if not self.has_border:
            logger.info(f"Window size {window.getmaxyx()} and length text = {len(self.text)}")
            # t = "-" * ( self.win.getmaxyx()[1] -1  )
            window.insstr(0,0,self.text)

        else:
            window.box()
            window.addstr(1,1,self.text)

        window.refresh()





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
        # curses.use_default_colors()

        # term_lines, term_cols = stdsrc.getmaxyx()
        # me = curses.newwin(term_lines,term_cols,0,0)
        #
        # me.bkgd(" ",curses.color_pair(1))
        #
        # ma = me.derwin(1,5,4,0)
        #
        # logger.info(f"me is {me.getmaxyx()}")
        # logger.info(f"ma is {ma.getmaxyx()}")
        # ma.insstr(0,0,"hell")
        #
        #
        # ma.refresh()
        # me.refresh()

        # a = curses.newwin(5,20,10,50)
        # a.addstr("are you coming")
        # a.bkgd(" ",curses.color_pair(1))
        # a.refresh()
        # stdsrc.refresh()
        #
        #
        #
        # while (True):
        #
        #     c = stdsrc.getch()
        #     if c == -1:
        #         continue
        #
        #     if c == curses.KEY_RESIZE:
        #         a.refresh()
        #
        #     a.addch(c)
        #     a.refresh()
        #




        screen_handler = ScreenHandler(stdsrc)

        screen_login = Screen("login")
        login_layout = Layout({"topy":5,"topx":20})
        texto = Label("Hello",push=Push(0,5,0,0),hasBorder=True,background=1)
        texto1 = Label("whatup",push=Push(0,0,0,0))

        login_layout.add_item(texto)
        login_layout.add_item(texto1)
        screen_login.add_layout(login_layout)
        screen_login.set_spotlight(login_layout)


        screen_handler.add_screen(screen_login)
        screen_handler.set_spotlight(screen_name_identifier="login")




        # menu2 = Menu(topx=10,topy=20)
        # manzana = Item(text="whatup?")
        # menu2.addItem(manzana)
        #
        #
        # menuHandler = ScreenHandler()
        #
        # 
        # menu = Menu(topx=10,topy=5,axis="horizontal")
        # login_item = Item(text="Log in (1)",margin=Margin(0,1,0,0),padding=Padding(2,2,2,2))
        # signup_item = Item(text="Sign up (2)",margin=Margin(0,1,0,0))
        # shit = Item(text="whatup",margin=Margin(0,0,0,0))
        # dogs = Item(text="Who let the dogs out?")
        #
        # def login_action():
        #     menu.hide()
        #     menuHandler.removeLight()
        #     menuHandler.set_spotlight("menu2")
        #     
        #
        #
        #     # stdsrc.refresh()
        # login_item.setAction(ord("1"),login_action)
        # menu.addItem(login_item)
        # menu.addItem(signup_item)
        # menu.addItem(shit)
        # menu.addItem(dogs)
        #
        #
        #
        #
        # menuHandler.add_screen("menu",menu)
        # menuHandler.add_screen("menu2",menu2)
        # menuHandler.set_spotlight("menu")



        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue

            screen_handler.handleKey(c)

            # screen_login.show()

            pass


Main()




