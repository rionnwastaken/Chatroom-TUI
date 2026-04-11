import curses
from enum import StrEnum,auto
from io import DEFAULT_BUFFER_SIZE
from types import NoneType
from typing import Callable, Dict,Literal, Tuple,TypedDict,Protocol,Required,NotRequired, Unpack
from abc import ABC, abstractmethod
import logging


logger:logging.Logger

'''
Spotlight is the current screen that receives the input
'''





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

        logger.info(f"Adding screen {screen.screen_name_identifier}")
        self.screens[screen.screen_name_identifier] = screen
        # self.set_spotlight(screen.screen_name_identifier)

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
            #

        screen:Screen | None = self.screens.get(screen_name_identifier)
        if screen == None:
            raise Exception(f"'{screen_name_identifier}' screen was not found\nMake sure the screen exists before setting it as spotlight")
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


# class LayoutApi(Protocol):
#     def traverse(self,direction:Literal["forward","backward"]) -> None: ...

class Screen():

    terminal_window:curses.window

    def __init__(self,screen_name_identifier,background=None) -> None:
        term_lines,term_cols = Screen.terminal_window.getmaxyx() 
        self.screen_window = curses.newwin(term_lines,term_cols,0,0)
        self.layouts:list["Layout"] = []
        self.spotlight:None | Layout = None
        self.traversal_index = -1 # Starts like that cause when adding layout it increments
        self.screen_name_identifier = screen_name_identifier
        self.background = background


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
        """
        Renders each layout
        Makes the layout spotlight handle_receiving_focus
        """


        for lay in self.layouts:
            lay.show()

        if self.background != None:
            self.screen_window.bkgd(" ",curses.color_pair(self.background))


        
        if self.spotlight != None: 
            self.spotlight.handle_receive_focus('forward')


        self.screen_window.refresh()

        logger.info(f"{'-'*5}RENDER LAYOUTS {'-'*5}")






    def set_spotlight(self,layout:"Layout"):



        self.spotlight = layout
        self.traversal_index = -1
        for index,layout in enumerate( self.layouts ):
            if self.spotlight == layout:
                self.traversal_index = index
                logger.info(f"Screen traversal index {self.traversal_index}")
                break

        if self.traversal_index == -1:
            raise Exception(f"Screen [{self.screen_name_identifier}]  func [set_spotlight] traversal_index was not found")


    def traverse(self,direction:Literal["forward","backward"]) :
        """ 

        Gives focus to the next layout
        if only 1 layout == giving focus to that same layout; calls -> layout_receive_focus(direction)
        """


        
        if len(self.layouts) == 1:
            self.layouts[0].handle_receive_focus(direction)
            return  

        logger.info("Screen, traversing to a new layout")

        


        magnitude = 1 if direction == "forward" else -1


        count = 0
        while (True):

            previous_layout:Layout = self.layouts[self.traversal_index]
            previous_layout.handle_lose_focus(direction)

            self.traversal_index += magnitude

            if self.traversal_index < 0:
                self.traversal_index = len(self.layouts) - 1

            if self.traversal_index >= len(self.layouts):
                self.traversal_index = 0 

            next_layout = self.layouts[self.traversal_index]
            logger.info(f"Next layout focusable? {self.layoutIsFocusable(next_layout)}")

            
            if self.layoutIsFocusable(next_layout):
                next_layout.handle_receive_focus(direction)
                self.spotlight = next_layout
                break

            count += 1
            if count >= len(self.layouts) + 5:
                raise Exception("class Screen func [traverse] There is error in travesal infinite while loop")

        return  

        # if (self.traversal)

    
    def layoutIsFocusable(self,layout:"Layout") -> bool:

        if isinstance(layout,FocusableLayout) or isinstance(layout,GlobalKeyLayout):
            return True

        return False

        



    def handleKey(self,c):
        if self.spotlight != None:
            # logger.info(f"Layout id {self.spotlight.id}")
            self.spotlight.handleKey(c)
            return

        raise Exception(f"class [Screen] func [handleKey] does not have a layout in spotlight")


class LayoutType(TypedDict,total=False):
    coordinates:Coordinates | None
    where:Where | None
    hasBorder:bool
    background:int
    axis:Literal["horizontal","vertical"]
    padding:Padding
    push:Push




class Layout(ABC):
    ''' 
    A layout is a window that holds items
    It calculates the  required dimensions to fit the items
    Parent of FocusableLayout and GlobalKeyLayout
    Layout creates the derevied windows for the Items
    '''
    def __init__(
        self,**kwargs:Unpack[LayoutType]
    ) -> None:

        self.id:int
        self.items:list["Item"] = [] 

        #focusable
        # self.traversal_index = -1

        self.axis = kwargs.get('axis') or 'horizontal'
        self.layout_window:curses.window

        self.hasBorder = kwargs.get('hasBorder') or True
        self.background = kwargs.get('background') or DefaultColors.LAYOUT_NORMAL

        self.padding = kwargs.get('padding') or Padding()
        self.push = kwargs.get('push') or Push()

        #Length,margins,padding everything
        self.total_width = 0 
        self.total_height = 0

        self.item_current_posx = 0
        self.item_current_posy = 0

        self.where = kwargs.get('where')
        self.coordinates = kwargs.get('coordinates')

        if self.coordinates != None:
            self.topx = self.coordinates["topx"]
            self.topy = self.coordinates["topy"]

        if self.where == None and self.coordinates == None:
            raise Exception("Currently it is not supported to automatically position a layout without coordinates or where   ")


        if self.where != None and self.coordinates != None:
            raise Exception("Cannot use where and coordinates at the same time")


        self.min_height = None
        self.min_width = None

        self.default_border_padding = 2


        self.screen_api:ScreenAPI



        self.registered_global_keys:Dict[int,Callable] = {}
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



        
        #TODO implement min width and maxwidth 

        
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


        if self.background != None:
            logger.info(f"Layout setting background {DefaultColors.LAYOUT_NORMAL}")
            self.layout_window.bkgd(" ",curses.color_pair(DefaultColors.LAYOUT_NORMAL))

        self.layout_window.refresh()


        # if isinstance(self.spotlight,FocusableItem):
        #     self.spotlight.handleGetFocus()

        logger.info(f"{'-'*10}END RENDERING LAYOUT{'-'*10}")
    

    def register_global_key(self,key:int | str,callable:Callable):
        """
        Meant to be used for keys like esc or arrowkeys
        """ 

        if isinstance(key,str):
            l = len(key)

            if len(key) > 1:
                raise Exception(f"Cannot register_global_key where key has length greater than 1. length: {key}")
            key = ord(key)


        if key in self.registered_global_keys:
            raise Exception(f"Cannot register the same key twice ({key},'{chr(key)}') in the same layout")

        self.registered_global_keys[key] = callable


    
    def add_item(self,item:"Item"):
        """
        Adds items to the layout
        self.win of the item is not yet created
        """

        allow,error = self.validate_item(item)

        if not allow:
            if isinstance(error,Exception):
                raise error
            
            raise Exception("In not allow it should raise error,fix it")


        item.layout_api = self
        self.items.append(item)


    @abstractmethod
    def validate_item(self,item:"Item") -> Tuple[bool,None | Exception]  :
        """
        True -> Item belongs to the layout
        False -> There is an error and program should raise Error
        """
        raise NotImplementedError()


    def handle_receive_focus(self,from_where:Literal["forward","backward"]):
        """ Can be overriden to hook more functionality """
        if self.hasBorder:
            self.layout_window.bkgd(" ",curses.color_pair(DefaultColors.LAYOUT_FOCUSED))
            self.layout_window.refresh()
        logger.info("Layout receive focus")


    def handle_lose_focus(self,from_where:Literal["forward","backward"]):
        """ Can be overriden to hook more functionality """
        if self.hasBorder:
            self.layout_window.bkgd(" ",curses.color_pair(DefaultColors.LAYOUT_NORMAL))
            self.layout_window.refresh()
        logger.info("Layout  losing focus")




    @abstractmethod
    def traverse(self,direction:Literal["forward","backward"]):
        pass


    def hide(self):
        self.layout_window.clear()
        self.layout_window.refresh()


    @abstractmethod
    def handleKey(self,c):
        raise NotImplementedError()


    def handleTraverseKey(self,c) -> bool:
        """True means is traversal and the caller should abort handling the key"""
        if c == ord("\t"):
            self.traverse("forward")
            return True

        if c == curses.KEY_BTAB:
            self.traverse("backward")
            return True

        return False






class FocusableLayout(Layout):
    """
    Can contain FocusableItem and DecorationItem
    Spotlight can only be FocusableItem
    """ 

    def __init__(
            self,**kwargs:Unpack[LayoutType]
    ) -> None:

        super().__init__(**kwargs)

    def add_item(self,item:"Item"):
        super().add_item(item)
        self.set_spotlight(item)

    def validate_item(self, item: "Item"):
        if isinstance(item,FocusableItem) or isinstance(item,DecorationItem):
            return True,None

        return False, Exception(f"Item {item.__class__.__name__} is not compatible with Layout {self.__class__.__name__}")


    def set_spotlight(self,item:"Item"):

        self.spotlight = item

        found = False
        for index,item in enumerate( self.items ):
            if self.spotlight == item:
                self.traversal_index = index
                found = True

        if not found:
            raise Exception(f"class [FocusableLayout]  func [set_spotlight] item was not found in items")


    def handleKey(self,c):

        if c in self.registered_global_keys:
            self.registered_global_keys[c]()
            return

        if self.handleTraverseKey(c):
            return

        if isinstance(self.spotlight,FocusableItem):
            self.spotlight.handleKey(c)



    def handle_receive_focus(self,from_where:Literal["forward","backward"]):

        logger.info("before calling supa")

        logger.info("after calling supa")


        if from_where == 'forward':
            self.traversal_index = 0
            self.spotlight = self.items[0]

        elif from_where == 'backward':
            self.traversal_index = len(self.items) -1
            self.spotlight = self.items[ self.traversal_index ]


        current_item = self.items[self.traversal_index]
        if isinstance(current_item,FocusableItem):
            logger.info(f"layout_receive_focus Widget receiving focus {current_item.__class__.__name__}")
            current_item.handleGetFocus()

        super().handle_receive_focus(from_where)

    def traverse(self,direction:Literal["forward","backward"]):
        """ 
        'forward' -> Traverse to next item
        'backward' -> Traverse to preceding item

        Going out either edge calls screen.traverse(direction)

        """
        
        logger.info(f"Traversing in Layout, and kind is {self.layout_kind}")


        magnitude = 1 if direction == "forward" else -1
        count = 0




        while (True):
            previous_item = self.items[self.traversal_index]

            if isinstance(previous_item,FocusableItem):
                previous_item.handleLoseFocus()

            self.traversal_index += magnitude

            if self.traversal_index < 0:
                is_there_next_layout = self.screen_api.traverse("backward")
                return




            #Go to next layout
            if self.traversal_index >= len(self.items):
                self.traversal_index = -1 
                is_there_next_layout = self.screen_api.traverse("forward")
                return



            next_item = self.items[self.traversal_index]

            if isinstance(next_item,FocusableItem):
                logger.info(f"traverse Widget receiving focus {next_item.__class__.__name__}")
                next_item.handleGetFocus()
                self.spotlight = next_item
                break

            count += 1
            if count >= len(self.items) + 5:
                raise Exception("class Layout func [traverse] There is error in travesal infinite while loop")




class GlobalKeyLayout(Layout):
    """
    Can contain GlobalKeyItem and DecorationItem
    """ 

    def handleKey(self,c):

        if c in self.registered_global_keys:
            self.registered_global_keys[c]()
            return


        if self.handleTraverseKey(c):
            return

        for item in self.items:
            if isinstance(item,GlobalKeyItem):
                global_key = item.global_key
                if c == global_key:
                    item.onAction()


    def validate_item(self, item: "Item"):
        if isinstance(item,GlobalKeyItem) or isinstance(item,DecorationItem):
            return True,None

        return False, Exception(f"Item {item.__class__.__name__} is not compatible with Layout {self.__class__.__name__}")

    def traverse(self,direction:Literal["forward","backward"]):
        """ 
        'forward' -> Traverse to next item
        'backward' -> Traverse to preceding item

        Going out either edge calls screen.traverse(direction)

        """
        logger.info(f"Traversing in Layout, and kind is {self.layout_kind}")
        self.screen_api.traverse(direction)




class DecorationLayout(Layout):
    """
    Layout that is not focusable , which means it cannot handle keys
    """
    pass






'''
Item can hold anything, it only cares about its dimensions 
Item is widget holder for example for labels ,inputs
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

        self.layout_api:Layout

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



class DecorationItem(Item,ABC):
    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)

    

'''
handleReceiving
'''
class FocusableItem(Item,ABC):

    # def __init__(self, lines: int, cols: int, push=Push(), padding=Padding(), hasBorder=False, background=None) -> None:
    def __init__(self,**kwargs) -> None:

        self.on_receive_focus:Callable | None = None
        self.on_lose_focus:Callable | None = None



        super().__init__(**kwargs)
        # Item.__init__(self,lines, cols, push, padding, hasBorder, background)

    def handleGetFocus(self):
        self.handleGetFocusDefault()
        if self.on_receive_focus != None:
            self.on_receive_focus()


        # return None

    def handleLoseFocus(self):
        self.handleLoseFocusDefault()
        if self.on_lose_focus != None:
            self.on_lose_focus()


    @abstractmethod
    def handleGetFocusDefault(self):
        return None

    @abstractmethod
    def handleLoseFocusDefault(self):
        return None

    @abstractmethod
    def handleKey(self,c):
        raise NotImplementedError()


class GlobalKeyItem(Item,ABC):
    """
    Item that does action when its global_key is pressed
    """

    # def __init__(self,global_key,lines: int, cols: int, push=Push(), padding=Padding(), hasBorder=False, background=None) -> None:
    def __init__(self,global_key,global_key_char,**kwargs) -> None:
        self.global_key = global_key
        super().__init__(**kwargs)
        # Item.__init__(self,lines, cols, push, padding, hasBorder, background)
        

    @abstractmethod
    def onAction(self):
        return None



class Label(DecorationItem):
    '''
    Item to just show text
    '''
    def __init__(self,text,**kwargs) -> None:
        self.length = len(text)
        self.text = text
        self.win:curses.window

        kwargs.setdefault('cols',self.length)
        kwargs.setdefault('lines',1)
        super().__init__(**kwargs)


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
        



    def renderItem(self,window:curses.window):
        self.win = window

        if self.background != None:
            self.win.bkgd(" ", curses.color_pair(self.background))

        else:
            #Use default color
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_NORMAL))

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

class defaultItemAttributes(TypedDict,total=False):
     push:Push
     padding:Padding
     hasBorder:bool
     background:int | None
     lines:int
     cols:int
     min_width:int
     max_width:int




class ButtonBaseType(defaultItemAttributes):
     text:Required[str]


class ButtonGlobalKeyType(ButtonBaseType,total=False):
     text:Required[str]
     global_key_char:Required[str]
     global_key:int






class ButtonGlobalKey(ButtonBase,GlobalKeyItem):

    def __init__(self,**kwargs:Unpack[ButtonGlobalKeyType]) -> None:




        global_key_char = kwargs.get('global_key_char')
        text = len(kwargs.get('text'))

        kwargs.setdefault("lines",1 )
        kwargs.setdefault("cols",text )

        if global_key_char == None:
            raise Exception(f"Error:global_key is None")

        if len(global_key_char) > 1:
            raise Exception(f"global key {global_key_char} must be a char")

        kwargs['global_key'] = ord(global_key_char)
        super().__init__(**kwargs)


    def onAction(self):
        if len( self.actions ) >0:
            for action in self.actions:
                action()

        pass


    

        


class ButtonFocusable(ButtonBase,FocusableItem):

    def __init__(self,**kwargs:Unpack[ButtonBaseType]) -> None:

        text =  kwargs.get('text') 

        kwargs.setdefault("lines",1 )
        kwargs.setdefault("cols",len(text))
        super().__init__(**kwargs)


        self.actions:dict = {} # type: ignore


    def addAction(self,key: str | int,callable: Callable): # type: ignore

        if isinstance(key,str):
            if len(key) != 1:
                raise Exception(f"addKeyAction, key length is {len(key)}")
            key = ord(key)
        
        logger.info(f"Adding key {key}")


        self.actions[key] = callable
        # return super().addAction(c)


    def handleGetFocusDefault(self):

        if self.has_border:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_FOCUSED))
            self.win.refresh()
            logger.info("focusablebutton chaning color")
        logger.info("button receiving focus")
        # print("shit")

    def handleLoseFocusDefault(self):
        if self.has_border:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_NORMAL))
            self.win.refresh()
        logger.info("button loosing focus")

    def handleKey(self, c):

        if c in self.actions:
            self.actions[c]()


        logger.info(f"Buttonfocusable handling key {c}")
        # print("handling")





class Input(FocusableItem):
    # def __init__(self,push=Push(),min_width=10, padding=Padding(),hasBorder=False,background=None) -> None:
    def __init__(self,**kwargs:Unpack[defaultItemAttributes]) -> None:

        min_width = kwargs.setdefault('min_width',10)

        self.filter = None
        self.length = kwargs.get('min_width')
        self.win:curses.window
        self.cursorx = -1 if not kwargs.get('hasBorder') else 0
        self.cursory = 0 if not kwargs.get('hasBorder') else 1
        self.max_line,self.max_col = -1,-1

        
        kwargs.setdefault('lines',1)
        kwargs.setdefault('cols',min_width)


        super().__init__(**kwargs)


    
    def handleGetFocusDefault(self):
        self.win.move(self.cursory,self.cursorx)
        self.win.refresh()
        return None

    def renderItem(self,window:curses.window):
        self.win = window

        if self.background != None:
            self.win.bkgd(" ", curses.color_pair(self.background))
#
        if self.has_border:
            window.box()
        self.max_line,self.max_col = window.getmaxyx()
        logger.info(f"info max_col es {self.max_col}")
        window.refresh()


    def getWin(self):
        return self.win

    def handleKey(self,c):
        logger.info(f"handling key in input {c}")

        




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


        if self.filter != None:
            should_allow_key = self.filter(c)

            if should_allow_key == False:
                return

            elif should_allow_key:
                pass

            else:
                raise Exception(f"Error in Input self.filter, it should return boolean but returned {type(should_allow_key)}")


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



#hey


if __name__ == "__main__":
    print(ButtonGlobalKey.mro())
