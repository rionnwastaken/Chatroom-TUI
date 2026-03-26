import curses
from enum import StrEnum,auto
from types import NoneType
from typing import Callable,Literal,TypedDict,Protocol,Required,NotRequired, Unpack
from abc import ABC, abstractmethod
import logging


logger:logging.Logger

'''
Spotlight is the current screen that receives the input
'''


class ReusableActions():


    def __init__(self,screenhandler:"ScreenHandler") -> None:
        self.screenhandler = screenhandler 
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
        self.traversal_index = -1 # Starts like that cause when adding layout it increments
        self.screen_name_identifier = screen_name_identifier


        self.id_counter = 0

    def get_screen_size(self):
        return self.screen_window.getmaxyx()

        
    def get_window(self):
        return self.screen_window



    def add_layout(self,layout:"Layout"):
        layout.screen_api = self
        layout.id = self.id_counter
        self.traversal_index += 1
        self.id_counter += 1
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
            logger.info(f"Layout id {self.spotlight.id}")
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
        padding=Padding(),
        push=Push(),
    ) -> None:

        self.id:int


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



        self.registered_global_keys = []
        self.layout_kind = None
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
    
    def register_global_key(self,key):
        if key in self.registered_global_keys:
            raise Exception(f"Cannot register the same key twice ({key},'{chr(key)}') in the same layout")

        self.registered_global_keys.append(key)


    def add_item(self,item:"Item"):

        if (isinstance(item,StaticItem)):
            pass

        elif (self.layout_kind != None and not isinstance(item,self.layout_kind)):
            raise Exception(f"Item is not subclass of {self.layout_kind}\nA layout should only have items of the same kind")



        if (isinstance(item,FocusableItem)):
            self.layout_kind = FocusableItem

        if (isinstance(item,GlobalKeyItem)):
            self.register_global_key(item.global_key)
            self.layout_kind = GlobalKeyItem


        self.items.append(item)

        if isinstance(item,FocusableItem):
            self.set_spotlight(item)


    def set_spotlight(self,item:"Item"):
        if isinstance(item,GlobalKeyItem): 
            raise Exception("class [Layout] func [set_spotlight] cannot set spotlight when item is of GlobalKeyItem")

        self.spotlight = item
        self.traversal_index = -1
        for index,item in enumerate( self.items ):
            if self.spotlight == item:
                self.traversal_index = index

        if self.traversal_index == -1:
            raise Exception(f"class [Layout]  func [set_spotlight] item was not found in items")


    def traverse(self,direction:Literal["forward","backward"]):

        #Request switching to another layout
        if self.layout_kind == GlobalKeyItem: 
            self.screen_api.traverse("forward")
            return


        magnitude = 1 if direction == "forward" else -1
        count = 0

        #No items
        # if len(self.items) <= 0:
        #     self.screen_api.traverse("forward")
        #     return



        while (True):
            previous_item = self.items[self.traversal_index]

            self.traversal_index += magnitude

            if self.traversal_index < 0:
                self.traversal_index = len(self.items) - 1


            #Go to next layout
            if self.traversal_index >= len(self.items):
                self.traversal_index = 0 
                self.screen_api.traverse("forward")
                logger.info("screen forward")
                return

            next_item = self.items[self.traversal_index]

            if isinstance(next_item,FocusableItem):
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

        if self.layout_kind == GlobalKeyItem: 
            found_item = False
            for item in self.items:
                #:
                if isinstance(item,GlobalKeyItem):
                    global_key = item.global_key
                    if c == global_key:
                        # logger.info("Found global key item")
                        found_item = True
                        item.onAction()
            # logger.info(f"Found item {found_item}, length items {len(self.items)}, c={c,chr(c)}")

        else:
            # logger.info("There are NO global keys")
            if isinstance(self.spotlight,FocusableItem):
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

    def __init__(
        self,
        lines:int,
        cols:int,
        push = Push(),
        padding = Padding(),
        hasBorder=False,
        background=None,
        min_width=None,
        max_width=None,
        **kwargs
    ) -> None:


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

    

class FocusableItem(Item,ABC):

    # def __init__(self, lines: int, cols: int, push=Push(), padding=Padding(), hasBorder=False, background=None) -> None:
    def __init__(self,**kwargs) -> None:

        super().__init__(**kwargs)
        # Item.__init__(self,lines, cols, push, padding, hasBorder, background)

    @abstractmethod
    def handleReceivingFocus(self):
        return None

    @abstractmethod
    def handleKey(self,c):
        raise NotImplementedError()


class GlobalKeyItem(Item,ABC):

    # def __init__(self,global_key,lines: int, cols: int, push=Push(), padding=Padding(), hasBorder=False, background=None) -> None:
    def __init__(self,global_key,global_key_char,**kwargs) -> None:
        self.global_key = global_key
        super().__init__(**kwargs)
        # Item.__init__(self,lines, cols, push, padding, hasBorder, background)

        

    @abstractmethod
    def onAction(self):
        return None

class StaticItem(Item):
    pass




'''Here lines and cols dont take into considerations the space of the window borders '''
class Label(StaticItem):
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







class ButtonBase(Item,ABC):
    def __init__(self,text,**kwargs) -> None:
        self.length = len(text)
        self.text = text

        self.win:curses.window
        self.actions:list[Callable] = []

        super().__init__(**kwargs)
        # self.item:Item
        # super().__init__(lines, cols, push, padding, hasBorder, background)

        



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




class ButtonGlobalKeyType(TypedDict,total=False):

     text:Required[str]
     global_key_char:Required[str]
     global_key:int
     push:Push
     padding:Padding
     hasBorder:bool
     background:int | None
     lines:int
     cols:int


class defaultItemAttributes(TypedDict,total=False):
     push:Push
     padding:Padding
     hasBorder:bool
     background:int | None
     lines:int
     cols:int
     min_width:int
     max_width:int




class ButtonGlobalKey(ButtonBase,GlobalKeyItem):

    def __init__(self,**kwargs:Unpack[ButtonGlobalKeyType]) -> None:




        global_key_char = kwargs.get('global_key_char')
        text = len(kwargs.get('text'))
        
        kwargs.setdefault("padding", Padding())
        kwargs.setdefault("push",Push() )
        kwargs.setdefault("hasBorder",False )
        kwargs.setdefault("background",None )
        kwargs.setdefault("lines",1 )
        kwargs.setdefault("cols",text )

        if global_key_char == None:
            raise Exception(f"Error:global_key is None")

        if len(global_key_char) > 1:
            raise Exception(f"global key {global_key_char} must be a char")

        # kwargs.pop('glo')
        kwargs['global_key'] = ord(global_key_char)

        # self, text,global_key:str, push=Push(), padding=Padding(), hasBorder=False, background=None,**kwargs


        # self.item = self

        super().__init__(**kwargs)

        # ButtonBase.__init__(self,text=text,**kwargs)
        # GlobalKeyItem.__init__(self,ord(global_key), 1,len(self.text), push, padding, hasBorder, background)
        # GlobalKeyItem.__init__(self, ord(global_key), len(self.text), push, padding, hasBorder, background, lines=1)




    def onAction(self):
        if len( self.actions ) >0:
            for action in self.actions:
                action()

        pass


    

        


class ButtonFocusable(ButtonBase,FocusableItem):


    # def __init__(self, text, push=Push(), padding=Padding(), hasBorder=False, background=None,**kwargs:Unpack[defaultItemAttributes]) -> None:
    def __init__(self,text,**kwargs:Unpack[defaultItemAttributes]) -> None:

        kwargs.setdefault('text',text)
        # self.item = self

        super().__init__(**kwargs)

        ButtonBase.__init__(self,text)
        FocusableItem.__init__(self, 1,len(self.text), push, padding, hasBorder, background)




    def handleReceivingFocus(self):
        print("shit")

    def handleKey(self, c):
        print("handling")


# b = ButtonFocusable("hey")
# a = ButtonGlobalKey("was",ord('a'))



class Input(FocusableItem):
    # def __init__(self,push=Push(),min_width=10, padding=Padding(),hasBorder=False,background=None) -> None:
    def __init__(self,**kwargs:Unpack[defaultItemAttributes]) -> None:

        min_width = kwargs.setdefault('min_width',10)


        self.length = kwargs.get('min_width')
        self.win:curses.window
        self.cursorx = -1 if not kwargs.get('hasBorder') else 0
        self.cursory = 0 if not kwargs.get('hasBorder') else 1
        self.max_line,self.max_col = -1,-1

        
        kwargs.setdefault('lines',1)
        kwargs.setdefault('cols',min_width)


        super().__init__(**kwargs)


        # super().__init__(
        #     1,
        #     self.length,
        #     push=push,
        #     padding=padding,
        #     hasBorder=hasBorder,
        #     background=background,
        # )


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
        if c == curses.KEY_ENTER or c == ord("\n"):
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




if __name__ == "__main__":
    print(ButtonGlobalKey.mro())
