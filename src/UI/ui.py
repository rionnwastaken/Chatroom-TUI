import curses
from enum import IntEnum, StrEnum,auto
from io import DEFAULT_BUFFER_SIZE
from types import NoneType
from typing import Callable, Dict,Literal, Tuple,TypedDict,Protocol,Required,NotRequired, Unpack
from abc import ABC, abstractmethod
import logging

from typing import cast
from UI.properties import Where,Padding,Push,Direction,Status
from UI.types import ButtonBaseType,Coordinates,LayoutType,ButtonGlobalKeyType,BaseType,ItemAttributesType, ScreenType
from pathlib import Path



filepath = Path(__file__).parent.parent.parent / "logs" / "TUI.log"
print(filepath)

with open(filepath,"w+") as f:
    f.write("")

class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra or {}


        class_name = str(extra.get("class_name",""))
        id = str(extra.get("id",""))
        

        class_name_full = class_name


        if id != "":
            class_name_full += f"({id})"

        extra.setdefault("class_full_name",class_name_full)

        

        kwargs.setdefault("extra",extra)
        return '%s' % (msg), kwargs

root = logging.getLogger(__name__)
root.setLevel(logging.DEBUG)
hand = logging.FileHandler(filepath)
formatter = logging.Formatter(fmt="%(class_full_name)s::%(levelname)s %(message)s")
hand.setFormatter(formatter)
root.addHandler(hand)


logger = CustomAdapter(root)



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


class Base(ABC):
    def __init__(self,**kwargs) -> None:
        self.id:object = kwargs.pop("id",None) 
        self.logger = CustomAdapter(root,{"class_name":self.__class__.__name__})
        super().__init__(**kwargs)





class GlobalFocusManager:
    """ """
    pass



class FocusManager:

    def __init__(self) -> None:
        self.clients:list["FocusableClient"]  = []
        self.pos = -1 #As clients are added, it increases, so to start with the correct index
        self.spotlight:FocusableClient | None = None


        self.logger = CustomAdapter(root,{"class_name":self.__class__.__name__})
        self.clients_map:dict[object,FocusableClient] = {}


        self.focus_parent:FocusManager | None = None


        self.should_empty_layout_be_focusable = False




    def __len__(self):
        """
        Length of self.clients
        """     
        return len(self.clients)

    def add_client(self,client:"Base"):
        if client == None:
            raise Exception("Error: Trying to add client that is None")

        if not isinstance(client,FocusableClient):
            raise Exception("Client is not instance of Focusable Client")


        self.clients.append(client)
        self.spotlight = client
        self.pos = self.pos + 1




        self.logger.info(f"Id is {client.id} | {type(client)} ")
        if client.id == None: return

        if self.clients_map.get(client.id) != None:
            raise Exception(f"Error: Adding client that has the same id as {self.clients_map.get(client.id)}")

        self.clients_map[client.id] = client

        self.logger.debug(f"Register client {client.id}")


    def tell_current_client_lose_focus(self):
        if self.spotlight != None:
            self.spotlight.handleLoseFocus(Direction.JUMP)
        pass


    def tell_current_client_gain_focus(self):
        if self.spotlight != None:
            self.spotlight.handleGetFocus(Direction.JUMP)
        pass
    
    
    def set_spotlight(self,client:"FocusableClient") -> Status:
        """
        Set the spotlight by reference
        """ 

        
        self.logger.info(f"Tell Current client lose focus {self.spotlight.__class__}")

        self.tell_current_client_lose_focus()

        if client not in self.clients:
            return Status.ERR

        index = self.clients.index(client)
        self.pos = index
        self.spotlight = client

        self.logger.info(f"Tell Current client gain focus {self.spotlight.__class__}")
        self.tell_current_client_gain_focus()
        
        return Status.OK

    def set_spotlight_byid(self,id:object):

        client = self.clients_map.get(id)

        if client == None:
            self.logger.debug(f"{list( self.clients_map.keys() )}")
            raise Exception(f"Error: Client could not be found with the id of {id}")

        status = self.set_spotlight(client)

        if status == Status.ERR:
            raise Exception(f"There was error when setting spotlight by id.The client with id {id} is not registered")


    def set_spotlight_first(self):
        self.tell_current_client_lose_focus()

        
        if len(self.clients) >= 1:
            self.pos = 0
            self.spotlight = self.clients[0]
            self.tell_current_client_gain_focus()

            self.logger.debug(f"Set spotlight first client")



    def set_spotlight_last(self):
        if len(self.clients) >= 1:
            self.tell_current_client_lose_focus()
            self.pos = len(self.clients) -1
            self.spotlight = self.clients[-1]
            self.tell_current_client_gain_focus()


    def move(self,direction:Direction):

        if self.spotlight != None:
            self.spotlight.handleLoseFocus(direction)

        previous_pos = self.pos
        power = 1 if direction == Direction.FORWARD else -1


        if len(self.clients ) >= 1:
            self.pos = (self.pos + power) % len(self.clients)
        



        """
        If we move passed  the edge and wind up in another layout
        """
        
        walked_off_the_edge = False
        

        
        #Has moved passed the edge
        if direction == Direction.FORWARD and previous_pos > self.pos:
            self.logger.debug(f"RIGHT EDGE; We have moved passed the right edge and parent is None ? {self.focus_parent == None }")
            self.pos = 0

            
            
            if self.focus_parent != None:
                self.focus_parent.move(direction)
                walked_off_the_edge = True

        if direction == Direction.BACKWARD and previous_pos < self.pos:
            self.logger.debug("FocusManager: LEFT EDGE; We have moved passed the left edge")
            self.pos = len(self.clients) -1
            if self.focus_parent != None:
                self.focus_parent.move(direction)
                walked_off_the_edge = True


        #Layout has only 1 item so pos always is the same
        if previous_pos == self.pos:
            if self.focus_parent != None:
                self.focus_parent.move(direction)
                walked_off_the_edge = True
     


    

        if len( self.clients ) >=1:
            self.spotlight = self.clients[self.pos]

        if not walked_off_the_edge and self.spotlight != None:
            self.spotlight.handleGetFocus(direction)


    def forward(self):
        self.move(Direction.FORWARD)



    def backward(self):
        self.move(Direction.BACKWARD)



class FocusableClient(ABC):


    def __init__(self, **kwargs:Unpack[BaseType]): 

        self.on_receive_focus:Callable | None = None
        self.on_lose_focus:Callable | None = None
        

        self.focus_parent: FocusManager | None = None

        

        

    def createFocus(self):
        if self.focus != None:
            raise Exception("Error: Trying to createFocus when it already existed")

        self.focus = FocusManager()
        return self.focus


    def handleGetFocus(self,direction:Direction):
        self.defaultHandleGetFocus(direction)
        if self.on_receive_focus != None:
            self.on_receive_focus()



    def handleLoseFocus(self,direction:Direction):
        self.defaultHandleLoseFocus(direction)
        if self.on_lose_focus != None:
            self.on_lose_focus()


    @abstractmethod
    def defaultHandleGetFocus(self,direction:Direction):
        return None

    @abstractmethod
    def defaultHandleLoseFocus(self,direction:Direction):
        return None

    @abstractmethod
    def handleKey(self,c):
        raise NotImplementedError()



class ScreenHandler():
    def __init__(self,terminal_window) -> None:
        Screen.terminal_window = terminal_window
        self.terminal_window = terminal_window
        self.spotlight:Screen | None = None
        self.screens:dict[str,Screen] = {}


        self.logger = CustomAdapter(root,{"class_name":self.__class__.__name__})
        self.focus = FocusManager()


    def add_screen(self,screen:"Screen"):

        self.focus.add_client(screen)
        self.logger.info(f"Add screen({screen.id})")

    def removeLight(self):
        self.spotlight = None


    def set_spotlight(self,screen:"Screen"):
        self.focus.set_spotlight(screen)


    def set_spotlight_byid(self,id):
        self.logger.debug(f"Set spotlight by id")
        self.focus.set_spotlight_byid(id)

    def handleKey(self,c):

        if self.focus.spotlight != None:
            self.focus.spotlight.handleKey(c)
            return

        self.logger.debug(f" Spotlight is None in handleKey")






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



# class LayoutApi(Protocol):


class Screen(Base,FocusableClient):

    terminal_window:curses.window

    def __init__(self,**kwargs:Unpack[ScreenType]) -> None:
        term_lines,term_cols = Screen.terminal_window.getmaxyx() 

        self.screen_window = curses.newwin(term_lines,term_cols,0,0)

        
        self.background = kwargs.pop("background",None)
        self.visible = False
        

        


        super().__init__(**kwargs)
        self.focus = FocusManager()
        

    def get_screen_size(self):
        return self.screen_window.getmaxyx()

        
    def get_window(self):
        return self.screen_window


    def defaultHandleGetFocus(self, direction: Direction):
        self.visible = True
        self.show()



    def defaultHandleLoseFocus(self, direction: Direction):
        self.visible = False
        self.screen_window.clear()
        self.screen_window.refresh()



    def add_layout(self,layout:"Layout"):
        layout.screen = self
        

        
        if isinstance(layout,FocusableClient):
            self.logger.info("Adding Focusable Layout")
            self.focus.add_client(layout)


            #Every client must know their parent
            layout.focus_parent = self.focus

            if layout.focus != None:
                layout.focus.focus_parent = self.focus


    def show(self):
        """
        Renders each layout
        Makes the layout spotlight handle_receiving_focus
        """

        

        self.logger.info(f"Screen is about to show")


        

        for client in self.focus.clients:
            layout = cast("Layout", client)
            layout.show()


        if self.background != None:
            self.screen_window.bkgd(" ",curses.color_pair(self.background))

        

        
        if self.focus.spotlight == None:
            self.focus.set_spotlight_first()
        else:
            self.focus.tell_current_client_gain_focus()

        self.screen_window.refresh()







    def set_spotlight(self,layout:"Layout"):


        self.logger.info(f"set_spotlight is focusableitem {isinstance(layout,FocusableClient)}")

        if isinstance(layout,FocusableClient):
            status = self.focus.set_spotlight(layout)
            if status == Status.ERR:
                raise Exception("Error: Trying to set spotlight to layout that is not registered in clients.\nMake sure you set the spotlight after the layout has been added to the screen")

            return


        raise Exception("Error: Cannot set spotlight to a a layout that is not a focusableClient")
            





    def traverse(self,direction:Direction) :
        """ 
        """
        self.focus.move(direction)

    

    def handleKey(self,c):

        if self.focus.spotlight != None:
            self.focus.spotlight.handleKey(c)
            return

        raise Exception(f"class Screen; Func [handleKey] does not have a layout in spotlight\nWeird a layout should have at least a layout")






class Layout(Base,ABC):
    ''' 
    A layout is a window that holds items
    It calculates the  required dimensions to fit the items
    Parent of FocusableLayout and GlobalKeyLayout
    Layout creates the derevied windows for the Items
    '''
    def __init__(self, **kwargs:Unpack[LayoutType]) -> None:



        self.postponed_functions = []

        self.items:list["Item"] = [] 
        self.is_rendered = False

        #focusable
        # self.traversal_index = -1

        self.axis = kwargs.get('axis') or 'horizontal'
        self.layout_window:curses.window

        self.hasBorder = kwargs.get('hasBorder') or False
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


        self.screen:Screen



        self.registered_global_keys:Dict[int,Callable] = {}
        self.layout_kind = None
        self.spotlight:Item | None = None


        
        
        

        super().__init__(**kwargs)



    def _create_layout_window(self) -> curses.window:

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
            self.logger.debug(f"max height {biggerst_height}")
            self.total_height += biggerst_height

        #Only has to as wide as the widest item
        elif self.axis == 'vertical':
            self.total_width += biggest_width
            self.logger.debug(f"max height {layout_height}")
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
                max_y,max_x = self.screen.get_screen_size()
                topx = int( (max_x / 2) - (self.total_width / 2) )
                topy = 10



        layout_window = self.screen.get_window().derwin(
            self.total_height,
            self.total_width,
            topy,
            topx
        )




        self.logger.debug(f"layout_window size {layout_window.getmaxyx()}")

        return layout_window

    def paint_layout(self):

        if self.hasBorder:
            self.layout_window.box()


        if self.background != None:
            self.logger.debug(f"Layout setting background {DefaultColors.LAYOUT_NORMAL}")
            self.layout_window.bkgd(" ",curses.color_pair(DefaultColors.LAYOUT_NORMAL))

        self.layout_window.noutrefresh()


    def show(
        self,
    ):
        if not self.is_rendered:
            self.is_rendered = True
            self.render()


        self.paint_layout()
        for item in self.items:
            item.paint_item()

        curses.doupdate()
        


    def render(self):

        self.logger.info(f"{'-'*10}RENDERING LAYOUT{'-'*10}")

        self.total_width = 0
        self.total_height = 0

        self.item_current_posx = 0
        self.item_current_posy = 0

        if len(self.items) <=0:
            self.logger.debug(f"Layout has no items in screen")
            self.layout_window = self._create_layout_window()
            return


        self.layout_window = self._create_layout_window()
        self.paint_layout()

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
            self.logger.debug(f"menuwin lines={a[0]} cols={a[1]}")
            self.logger.debug(f"itemwin lines={win_lines} cols={win_cols} posy={self.item_current_posy} posx={self.item_current_posx} ")

            item_win:curses.window = self.layout_window.derwin(
                win_lines,
                win_cols,
                self.item_current_posy,
                self.item_current_posx
            )

            item.set_win(item_win)
            item.paint_item()

        
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


        
        
        

        


        
        

        self.logger.info(f"{'-'*10}END RENDERING LAYOUT{'-'*10}")
    

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


    
    """
    Returns last item
    """
    def add_items(self,*items:"Item") -> "Item":
        """
        Adds items to the layout
        self.win of the item is not yet created
        """

        if len(items) <= 0:
            raise Exception("Error in add_items: There were no items prompted")


        for item in items:
            allow,error = self.validate_item(item)

            if not allow:
                if isinstance(error,Exception):
                    raise error
                

            item.layout_api = self
            self.items.append(item)


        

        return items[-1]



    @abstractmethod
    def validate_item(self,item:"Item") -> Tuple[bool,None | Exception]  :
        """
        True -> Item belongs to the layout
        False -> There is an error and program should raise Error
        """
        raise NotImplementedError()


    def handle_receive_focus(self,from_where:Direction):
        """ Can be overriden to hook more functionality """
        if self.hasBorder:
            self.layout_window.bkgd(" ",curses.color_pair(DefaultColors.LAYOUT_FOCUSED))
            self.layout_window.refresh()
        self.logger.debug("Layout receive focus")


    def handle_lose_focus(self,from_where:Direction):
        """ Can be overriden to hook more functionality """
        if self.hasBorder:
            self.layout_window.bkgd(" ",curses.color_pair(DefaultColors.LAYOUT_NORMAL))
            self.layout_window.refresh()
        self.logger.debug("Layout  losing focus")



    def hide(self):
        self.layout_window.clear()
        self.layout_window.refresh()



class FocusableLayout(Layout,FocusableClient):
    """
    Can contain FocusableItem and DecorationItem
    Spotlight can only be FocusableItem
    """ 

    def __init__(self, **kwargs:Unpack[LayoutType]) -> None:
        super().__init__(**kwargs)


        self.focus = FocusManager()
        

    def add_items(self,*items:"Item"):
        last_item = super().add_items(*items)

        for item in items:
            if isinstance(item,FocusableClient):
                self.focus.add_client(item)

        

        if len(self.focus) <=0:
            raise Exception("Error:It doesnt make sense that focusablelayout has 0 focusableitems")


        
        
        return last_item

        

    def validate_item(self, item: "Item"):
        if isinstance(item,FocusableClient) or isinstance(item,DecorationItem):
            return True,None

        return False, Exception(f"Item {item.__class__.__name__} is not compatible with Layout {self.__class__.__name__}")


    def set_spotlight(self,item:"Item"):

        if not isinstance(item,FocusableClient):
            raise Exception("Error: Trying to set spotlight to item that is not a FocusableClient")


        if self.screen.visible:
            self.focus.set_spotlight(item)

        else:
            # self.focus.spotlight = 
            self.postponed_functions.append(lambda:self.focus.set_spotlight(item))




    def handleKey(self,c):

        if c in self.registered_global_keys:
            self.registered_global_keys[c]()
            return


        if c == ord("\t") or c == curses.KEY_BTAB:
            direction = Direction.FORWARD if c == ord("\t") else Direction.BACKWARD 
            self.focus.move(direction)
            return

        
        if self.focus.spotlight == None:
            return
        self.focus.spotlight.handleKey(c)


    
    def defaultHandleGetFocus(self, direction: Direction):

        super().handle_receive_focus(direction)

        if self.focus.spotlight != None:
            self.focus.tell_current_client_gain_focus()
            return


        if direction == Direction.FORWARD:
            self.focus.set_spotlight_first()
    

        if direction == Direction.BACKWARD:
            self.focus.set_spotlight_last()


        if direction == Direction.JUMP:
            self.focus.set_spotlight_first()


    def defaultHandleLoseFocus(self, direction: Direction):
        super().handle_lose_focus(direction)
        self.focus.tell_current_client_lose_focus()


class GlobalKeyLayout(Layout,FocusableClient):
    """
    Can contain GlobalKeyItem and DecorationItem
    """ 


    def __init__(self, **kwargs:Unpack[LayoutType]) -> None:
        super().__init__(**kwargs)
        self.focus = FocusManager()

    def handleKey(self,c):

        if c in self.registered_global_keys:
            self.registered_global_keys[c]()
            return



        if c == ord("\t") or c == curses.KEY_BTAB:
            direction = Direction.FORWARD if c == ord("\t") else Direction.BACKWARD 
            self.focus_parent.move(direction)
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



    def defaultHandleGetFocus(self, direction: Direction):

        super().handle_receive_focus(direction)

    def defaultHandleLoseFocus(self, direction: Direction):
        super().handle_lose_focus(direction)



class DecorationLayout(Layout):
    """
    Layout that is not focusable , which means it cannot handle keys
    """
    pass






'''
Item can hold anything, it only cares about its dimensions 
Item is widget holder for example for labels ,inputs
'''
class Item(Base,ABC):

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

        super().__init__(**kwargs)


    def set_win(self,win:curses.window):
        self.win = win

    def get_total_space(self) -> tuple[int,int]:
        lines = self.lines + self.push.bottom + self.push.top +  self.padding.top + self.padding.bottom
        cols = self.cols + self.push.right + self.push.left + self.padding.right + self.padding.left

        return (lines,cols)

    
    
    def paint_background(self):
        if self.background != None:
            self.win.bkgd(" ", curses.color_pair(self.background))

        else:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_NORMAL))

    def paint_insert_text_inside_border(self,text):

        if not self.has_border:
            self.logger.info(f"self.win size {self.win.getmaxyx()} and length text = {len(text)}")
            self.win.insstr(0,0,text)

        else:
            self.win.box()
            self.win.addstr(1,1,text)



    def paint_item(self):
        self.clear()
        self.paint()
        self.win.noutrefresh()

    @abstractmethod
    def paint(self):
        raise NotImplementedError()

    def show(self):
        self.logger.info("Showing item")
        self.paint()
        

    def clear(self):
        self.win.clear()
        self.win.noutrefresh()
        



class DecorationItem(Item,ABC):
    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)

    

class GlobalKeyItem(Item,ABC):
    """
    Item that does action when its global_key is pressed
    """

    
    def __init__(self,global_key,global_key_char,**kwargs) -> None:
        self.global_key = global_key
        super().__init__(**kwargs)
        
        

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


    def paint(self):

        self.paint_background()
        self.paint_insert_text_inside_border(self.text)








class ButtonBase(Item):
    def __init__(self,text,**kwargs) -> None:
        self.length = len(text)
        self.text = text

        self.win:curses.window
        self.actions:list[Callable] = []

        super().__init__(**kwargs)
        



    def paint(self):

        self.paint_background()
        self.paint_insert_text_inside_border(self.text)


        


    def getWin(self):
        return self.win

    def addAction(self,c:Callable):
        self.actions.append(c)







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


    

        


class ButtonFocusable(ButtonBase,FocusableClient):

    def __init__(self,**kwargs:Unpack[ButtonBaseType]) -> None:

        text =  kwargs.get('text') 

        kwargs.setdefault("lines",1 )
        kwargs.setdefault("cols",len(text))
        super().__init__(**kwargs)



        self.logger.info("init")
        self.actions:dict = {} # type: ignore


    def addAction(self,key: str | int,callable: Callable): # type: ignore

        if isinstance(key,str):
            if len(key) != 1:
                raise Exception(f"addKeyAction, key length is {len(key)}")
            key = ord(key)
        
        self.logger.info(f"Adding key {key}")


        self.actions[key] = callable
        


    def defaultHandleGetFocus(self,direction:Direction):

        if self.has_border:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_FOCUSED))
            self.win.refresh()
            self.logger.info("focusablebutton chaning color")
        self.logger.info("button receiving focus")
        

    def defaultHandleLoseFocus(self,direction:Direction):
        if self.has_border:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_NORMAL))
            self.win.refresh()
        self.logger.info("button loosing focus")

    def handleKey(self, c):

        if c in self.actions:
            self.actions[c]()


        self.logger.info(f"Buttonfocusable handling key {c}")
        





#TODO fix rendering
class Input(Item,FocusableClient):
    def __init__(self,**kwargs:Unpack[ItemAttributesType]) -> None:

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


    

    def defaultHandleGetFocus(self,direction:Direction):

        self.win.move(self.cursory,self.cursorx)
        self.win.refresh()

        if self.has_border:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_FOCUSED))
            self.win.refresh()
            self.logger.info("Input changes color")
        self.logger.info("button receiving focus")

    def defaultHandleLoseFocus(self,direction:Direction):


        if self.has_border:
            self.win.bkgd(" ", curses.color_pair(DefaultColors.WIDGET_NORMAL))
            self.win.refresh()
        self.logger.info("Input loosing focus")




    def paint(self):
        self.paint_background()

        if self.has_border:
            self.win.box()
        self.max_line,self.max_col = self.win.getmaxyx()
        self.logger.info(f"info max_col es {self.max_col}")


    def getWin(self):
        return self.win

    def handleKey(self,c):
        self.logger.info(f"handling key in input {c}")

        




        if c == curses.KEY_ENTER or c == ord("\n"):
            return
        
        if c == curses.KEY_BACKSPACE:

            if self.has_border:
                if self.cursorx <= 0:
                    return

            if self.cursorx < 0:
                return
            
            

            self.win.move(self.cursory,self.cursorx)
            self.win.addch(" ")
            self.win.move(self.cursory,self.cursorx)
            self.cursorx += -1
            
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
        
        self.win.refresh()






if __name__ == "__main__":
    print(ButtonGlobalKey.mro())
