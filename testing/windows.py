from ast import Nonlocal, Tuple
import curses
from enum import StrEnum,auto
import logging
import math
import _thread
from os import terminal_size
import time
import curses.textpad
import curses.panel
import time
from typing import Callable,Literal,TypedDict,Protocol
from abc import ABC, abstractmethod

logger = logging.getLogger()
logging.basicConfig(filename='window.log', level=logging.INFO)

with open("./window.log","w") as f:
    f.write("")



'''
Spotlight is the current screen that receives the input
'''


class ReusableActions():


    def __init__(self,screenhandler:"ScreenHandler") -> None:
        self.screenhandler = screenhandler 
        pass


    @staticmethod
    def changeColor(btn: "Button", cols: list | None = None):
        if cols is None:
            cols = [4, 5]
        x = -1  # fresh x per changeColor(btn) call ✓

        def inner():
            nonlocal x
            win = btn.getWin()
            x = (x + 1) % len(cols)
            win.bkgd(" ", curses.color_pair(cols[x]))
            win.refresh()
            btn.background = cols[x]
            logger.info(f"Changing btn color {cols[x]}")
        return inner


    def changeScreen(self,screen_identifier:str):
        def inner():
            logger.info("Changing screen?")
            self.screenhandler.set_spotlight(screen_identifier)  
        return inner




class Where(StrEnum):
    CENTER_OF_SCREEN = auto()

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
        self.set_spotlight(screen.screen_name_identifier)

    def removeLight(self):
        self.spotlight = None

    def draw(self):
        if self.spotlight == None:
            raise Exception(f"Screen spotlight is None")
        self.spotlight.get_window().clear()
        self.spotlight.get_window().refresh()
        self.spotlight.show()


    def set_spotlight(self,screen_name_identifier):

        #clear previous window
        if self.spotlight != None:
            self.spotlight.get_window().clear()
            self.spotlight.get_window().refresh()
            # self.terminal_window.clear()
            # self.terminal_window.refresh()
            #

        screen:Screen | None = self.screens.get(screen_name_identifier)
        if screen == None:
            raise Exception(f"'{screen_name_identifier}' screen was not found")
        self.spotlight = screen
        self.spotlight.show()

    def handleKey(self,c):
        if self.spotlight != None:
            self.spotlight.handleKey(c)
            return

        logger.info(f"Screen Spotligh is None ins handleKey")





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

class ScreenAPI(Protocol):
    def get_screen_size(self) -> tuple[int, int]: ...
    def traverse(self,direction:Literal["forward","backward"]) -> None: ...
    def get_window(self) -> curses.window: ...

class Screen():

    terminal_window:curses.window

    def __init__(self,screen_name_identifier) -> None:
        term_lines,term_cols = Screen.terminal_window.getmaxyx() 
        self.screen_window = curses.newwin(term_lines,term_cols,0,0)
        self.layouts:list["Layout"] = []
        self.spotlight:None | Layout = None
        self.traversal_index = 0
        self.screen_name_identifier = screen_name_identifier

    def get_screen_size(self):
        return self.screen_window.getmaxyx()

        
    def get_window(self):
        return self.screen_window



    def add_layout(self,layout:"Layout"):
        layout.screen_api = self
        self.layouts.append(layout)

        self.spotlight = layout


    def show(self):

        for lay in self.layouts:
            lay.show()
        self.screen_window.bkgd(" ",curses.color_pair(1))
        self.screen_window.refresh()

        logger.info(f"{'-'*5}RENDER LAYOUTS {'-'*5}")






    def set_spotlight(self,layout:"Layout"):



        self.spotlight = layout
        self.traversal_index = -1
        for index,lay in enumerate( self.layouts ):
            if self.spotlight == lay:
                self.traversal_index = index
                logger.info(f"Screen traversal index {self.traversal_index}")
                break

        if self.traversal_index == -1:
            raise Exception(f"Screen [{self.screen_name_identifier}]  func [set_spotlight] traversal_index was not found")


    def traverse(self,direction:Literal["forward","backward"]):
        logger.info("Screen, traversing to a new layout")

        magnitude = 1 if direction == "forward" else -1


        count = 0
        while (True):
            self.traversal_index += magnitude

            if self.traversal_index < 0:
                self.traversal_index = len(self.layouts) - 1

            if self.traversal_index >= len(self.layouts):
                self.traversal_index = 0 

            next_layout = self.layouts[self.traversal_index]
            logger.info(f"Next layout focusable? {next_layout.focusable}")
            if next_layout.focusable:
                self.spotlight = next_layout
                break

            count += 1
            if count >= len(self.layouts) + 5:
                raise Exception("class Screen func [traverse] There is error in travesal infinite while loop")

        return None

        # if (self.traversal)




    def handleKey(self,c):
        if self.spotlight != None:
            self.spotlight.handleKey(c)
            return

        raise Exception(f"class [Screen] func [handleKey] does not have a layout in spotlight")




''' 
A layout is a window that holds items
It calculates the  required dimensions to fit the items
It controls which item receives the keystroke
A layout can only of one type; focusable or have global keys which means when a layout has focus , it should contain
items only of one type but it can also have of no type (labels for example)


Layout creates the derevied windows for the Items

'''
class Layout():
    def __init__(
        self,
        coordinates:Coordinates | None  = None,
        where:Where | None = None,
        focusable=True,
        hasBorder=False,
        axis:Literal["horizontal","vertical"] = "horizontal",
        global_keys = False,
        padding=Padding(),
        push=Push(),
    ) -> None:
        self.focusable = focusable
        self.items:list["Item"] = []
        self.axis = axis
        self.traversal_index = 0
        self.layout_window:curses.window

        self.hasBorder = hasBorder

        self.padding = padding
        self.push = push

        #Length,margins,padding everything
        self.total_width = 0 
        self.total_height = 0

        self.item_current_posx = 0
        self.item_current_posy = 0

        self.where = where
        self.coordinates = coordinates
        if coordinates != None:
            self.topx = coordinates["topx"]
            self.topy = coordinates["topy"]

        if self.where == None and self.coordinates == None:
            raise Exception("Currently it is not supported to automatically position a layout without coordinates or where   ")


        if self.where != None and self.coordinates != None:
            raise Exception("Cannot use where and coordinates at the same time")




        self.axis = axis
        self.min_height = None
        self.min_width = None

        self.default_border_padding = 2


        self.screen_api:ScreenAPI
        # self.screen_window:curses.window
        # self.screen_obj:Screen



        self.there_are_global_keys = global_keys

        self.spotlight:Item | None = None




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


        self.total_height += self.padding.top + self.padding.bottom
        self.total_width += self.padding.right + self.padding.left

        self.item_current_posy += self.padding.top
        self.item_current_posx += self.padding.left



        

        
        # if self.min_width != None and self.total_width < self.min_width:
        #     self.total_width = self.min_width
        #
        # if self.min_height != None and self.total_height < self.min_height:
        #     self.total_height = self.min_height


        # self.total_height += 10
        # self.total_width += 10

        if self.hasBorder:
            self.total_height += self.default_border_padding
            self.total_width += self.default_border_padding
            self.item_current_posy +=1
            self.item_current_posx += 1


        topx = 0
        topy = 0

        if self.coordinates != None:
            topx = self.topx
            topy = self.topy

        if self.where != None:
            if self.where == Where.CENTER_OF_SCREEN:
                max_y,max_x = self.screen_api.get_screen_size()
                topx = int( (max_x / 2) - (self.total_width / 2) )
                topy = 10



        self.layout_window = self.screen_api.get_window().derwin(
            self.total_height,
            self.total_width,
            topy,
            topx
        )


        if self.hasBorder:
            self.layout_window.box()


        logger.info(f"layout_window size {self.layout_window.getmaxyx()}")

    def show(self):
        self._render()


    def _render(self):

        logger.info(f"{'-'*10}RENDERING LAYOUT{'-'*10}")

        self.total_width = 0
        self.total_height = 0

        self.item_current_posx = 0
        self.item_current_posy = 0

        if len(self.items) <=0:
            logger.info(f"Layout has no items in screen")
            return


        self._create_menu_window()

        if self.layout_window == None:
            raise Exception("Layout window is null")


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

                

            a  = self.layout_window.getmaxyx()
            logger.info(f"menuwin lines={a[0]} cols={a[1]}")
            logger.info(f"itemwin lines={win_lines} cols={win_cols} posy={self.item_current_posy} posx={self.item_current_posx} ")

            item_win:curses.window = self.layout_window.derwin(
                win_lines,
                win_cols,
                self.item_current_posy,
                self.item_current_posx
            )

            item.renderItem(item_win)

        
            if self.axis == 'horizontal':
            
                self.item_current_posx += sum([
                    width,
                    margin.get_push_horizontal_points(),
                    padding.get_padding_horizontal_points(),
                    border,
                    
                ]) 

            if self.axis == 'vertical':
                self.item_current_posy  += sum([
                    item_win.getmaxyx()[0],        
                    margin.bottom,
                    # padding.bottom
                    ])

        self.layout_window.bkgd(" ",curses.color_pair(2))
        self.layout_window.refresh()

        logger.info(f"{'-'*10}END RENDERING LAYOUT{'-'*10}")
    


    def add_item(self,item:"Item"):
        if self.there_are_global_keys and item.focusable:
            raise Exception("class [Layout] func [add_item] cannot add item that is focusable when there are global keys")

        self.items.append(item)

        if item.focusable:
            self.set_spotlight(item)


    def set_spotlight(self,item:"Item"):
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

        #Request switching to another layout
        if self.there_are_global_keys:
            self.screen_api.traverse("forward")
            return


        magnitude = 1 if direction == "forward" else -1
        count = 0

        while (True):
            previous_item = self.items[self.traversal_index]

            self.traversal_index += magnitude

            if self.traversal_index < 0:
                self.traversal_index = len(self.items) - 1


            #Go to next layout
            if self.traversal_index >= len(self.items):
                self.traversal_index = 0 
                self.screen_api.traverse("forward")

            next_item = self.items[self.traversal_index]
            if next_item.focusable:
                next_item.handleReceivingFocus()
                self.spotlight = next_item
                break

            count += 1
            if count >= len(self.items) + 5:
                raise Exception("class Layout func [traverse] There is error in travesal infinite while loop")


    def hide(self):
        self.layout_window.clear()
        self.layout_window.refresh()


    def handleKey(self,c):

        if c == ord("\t"):
            self.traverse("forward")
            return

        if self.there_are_global_keys:
            found_item = False
            for item in self.items:
                #:
                if item.global_key != None:
                    global_key = item.global_key
                    if c == global_key:
                        # logger.info("Found global key item")
                        found_item = True
                        item.onAction()
            # logger.info(f"Found item {found_item}, length items {len(self.items)}, c={c,chr(c)}")

        else:
            # logger.info("There are NO global keys")
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
class Item(ABC):

    def __init__(self,lines:int,cols:int,focusable = False,global_key = None,push = Push(),padding = Padding(),hasBorder=False,background=None) -> None:

        if focusable and global_key != None:
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

    def handleReceivingFocus(self):
        return None


    def handleKey(self,c):
        raise NotImplementedError()

    def onAction(self):
        return None
    



'''Here lines and cols dont take into considerations the space of the window borders '''
class Label(Item):
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



class Button(Item):
    def __init__(self,text,push=Push(), padding=Padding(),hasBorder=False,background=None,global_key = None,) -> None:
        self.length = len(text)
        self.text = text
        self.win:curses.window
        self.actions:list[Callable] = []
        super().__init__(
            1,
            self.length,
            push=push,
            padding=padding,
            hasBorder=hasBorder,
            background=background,
            global_key=global_key,
            focusable = False
        )


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


    def getWin(self):
        return self.win

    def addAction(self,c:Callable):
        self.actions.append(c)

    def onAction(self):
        if len( self.actions ) >0:
            for action in self.actions:
                action()

        pass

class Input(Item):
    def __init__(self,push=Push(),min_width=10, padding=Padding(),hasBorder=False,background=None) -> None:
        self.length = min_width
        self.win:curses.window
        self.cursorx = -1 if not hasBorder else 0
        self.cursory = 0 if not hasBorder else 1
        self.max_line,self.max_col = -1,-1



        super().__init__(
            1,
            self.length,
            push=push,
            padding=padding,
            hasBorder=hasBorder,
            focusable=True,
            background=background,
            global_key=None
        )


    def handleReceivingFocus(self):
        self.win.move(self.cursory,self.cursorx)
        return None

    def renderItem(self,window:curses.window):
        self.win = window

        if self.background != None:
            self.win.bkgd(" ", curses.color_pair(self.background))

        if self.has_border:
            window.box()
        self.max_line,self.max_col = window.getmaxyx()
        logger.info(f"info max_col es {self.max_col}")
        window.refresh()


    def getWin(self):
        return self.win

    def handleKey(self,c):
        logger.info(f"handling key in input {c}")

        logger.info(f"c {c}")
        if c == curses.KEY_ENTER or c == 10:
            return

        
        if c == curses.KEY_BACKSPACE:

            if self.has_border:
                if self.cursorx <= 0:
                    return

            if self.cursorx < 0:
                return
            
            # self.win.delch(self.cursory,self.cursorx)

            self.win.move(self.cursory,self.cursorx)
            self.win.addch(" ")
            self.win.move(self.cursory,self.cursorx)
            self.cursorx += -1
            # self.win.move(self.cursory,self.cursorx)
            self.win.refresh()
            return


        self.cursorx += 1

        if self.has_border:
            if self.cursorx >= self.max_col-2:
                self.cursorx  = self.max_col -3
                return

        
        if self.cursorx >= self.max_col-1:
            self.cursorx  = self.max_col -2
            return

        self.win.move(self.cursory,self.cursorx)
        self.win.addch(self.cursory,self.cursorx,c)
        # self.win.insch(c)
        self.win.refresh()






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
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_YELLOW)


        logger.info(f"COlors are : ?{ curses.COLOR_WHITE,curses.COLOR_BLUE }")




    def main(self,stdsrc:curses.window):
        self.init_colors()
        stdsrc.timeout(100)
        curses.mousemask(curses.BUTTON1_CLICKED)
        curses.mouseinterval(0)

        stdsrc.refresh()











        screen_handler = ScreenHandler(stdsrc)
        reusable_actions = ReusableActions(screen_handler)


        def create_signup_login_screen():
            screen = Screen("signup_login")
            layout = Layout(
                where=Where.CENTER_OF_SCREEN,
                axis='vertical',
                global_keys=True,
                focusable=True,
                hasBorder=False,
                padding=Padding(2,2,2,2)
            )
            btn = Button("Log in (1)",background=1,hasBorder=True,global_key=ord('1'))
            btn1 = Button("Sign in (2)",background=1,hasBorder=True,global_key=ord('2'))


            # btn.addAction(ReusableActions.changeColor(btn))
            btn1.addAction(ReusableActions.changeColor(btn1))

            btn.addAction(reusable_actions.changeScreen("signup"))


            layout.add_item(btn)
            layout.add_item(btn1)

            screen.add_layout(layout)


            other = Layout(coordinates={"topx":10,"topy":10},global_keys=True)
            e = Button("Press 'a'",hasBorder=True,background=2,global_key=ord('a'))
            other.add_item(e)
            e.addAction(ReusableActions.changeColor(e))

            screen.add_layout(other)




            screen.set_spotlight(layout)

            screen_handler.add_screen(screen)

        def create_signup():
            screen = Screen(screen_name_identifier="signup")
            layout = Layout(global_keys=True,where=Where.CENTER_OF_SCREEN)
            btn = Button("press 'a'",hasBorder=True,global_key=ord('a'))
            btn_color = Button("press 'b'",hasBorder=True,background=3,global_key=ord('b'))

            def s():
                screen_handler.set_spotlight("signup_login")

            btn.addAction(s)



            btn_color.addAction(ReusableActions.changeColor(btn_color))


            layout.add_item(btn)
            layout.add_item(btn_color)
            screen.add_layout(layout)


            screen.set_spotlight(layout)


            screen_handler.add_screen(screen)

        # name = "screen"
        # for i in range(0,5):
        #     logger.info(f"{name}{i}")
        #     screen = Screen(screen_name_identifier=f"{name}{i}")
        #     layout = Layout(global_keys=True,where=Where.CENTER_OF_SCREEN)
        #     btn = Button(f"{name}{i}",global_key=ord( 'n' ),hasBorder=True,background=3)
        #
        #     if i+1 >=5:
        #         i= 0
        #
        #     next_screen = f"{name}{i+1}"
        #     btn.addAction(reusable_actions.changeScreen(next_screen))
        #
        #
        #     layout.add_item(btn)
        #     screen.add_layout(layout)
        #
        #     screen.set_spotlight(layout)
        #     
        #
        #     screen_handler.add_screen(screen)
        # screen_handler.set_spotlight("screen0")

        


        screen = Screen(screen_name_identifier="i")
        layout =  Layout(focusable=True,axis="vertical",where=Where.CENTER_OF_SCREEN)

        input_name = Input(hasBorder=True,min_width=10,background=2)
        label =  Label("Nombre:")

        layout.add_item(label)
        layout.add_item(input_name)
        input_lastname = Input(hasBorder=True,min_width=10,background=2)
        label =  Label("Last Name:")

        layout.add_item(label)
        layout.add_item(input_lastname)



        layout_gords =  Layout(focusable=True,axis="horizontal",coordinates={"topx":50,"topy":5})
        input_gorditas = Input(hasBorder=True,min_width=10,background=2)
        label =  Label("Nombre:")

        layout_gords.add_item(label)
        layout_gords.add_item(input_gorditas)
        input_chetos = Input(hasBorder=True,min_width=10,background=2)
        label =  Label("Last Name:")

        layout_gords.add_item(label)
        layout_gords.add_item(input_chetos)






        screen.add_layout(layout_gords)
        screen.add_layout(layout)
        screen_handler.add_screen(screen)











        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue


            if c == curses.KEY_RESIZE:
                screen_handler.draw()
                logger.info(f"NEW SIZE {stdsrc.getmaxyx()}")



            screen_handler.handleKey(c)

            # screen_login.show()

            pass


Main()




