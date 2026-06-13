import curses
from typing import Callable, Dict,Literal, Tuple,TypedDict,Protocol,Required,NotRequired, Unpack
from abc import ABC, abstractmethod
import logging

from typing import cast
from UI.properties import Where,Padding,Push,Direction,Status
from UI.types import ButtonBaseType,Coordinates,LayoutType,ButtonGlobalKeyType,BaseType,ItemAttributesType, ScreenType
from pathlib import Path
from UI.utils import CustomAdapter,root_logger_name,initialize_root_logger

from UI.misc import FocusableClient,FocusManager,GlobalFocusManager


from UI.colors import DefaultColors
from UI.bases import Base,Item,Layout, RenderAttributes




root = logging.getLogger(root_logger_name)
logger = CustomAdapter(root)


defaultcolors = DefaultColors.get_instance()


'''
Spotlight is the current screen that receives the input
'''

class ScreenHandler(Base):
    def __init__(self,terminal_window) -> None:
        Screen.terminal_window = terminal_window
        self.terminal_window = terminal_window
        self.spotlight:Screen | None = None
        self.screens:dict[str,Screen] = {}

        self.global_actions:dict[int,Callable] = {}


        kwargs = {
                "id":"root"
                }

        super().__init__(**kwargs)
        self.focus = FocusManager(self.class_name,self.id)


    def add_screen(self,screen:"Screen"):

        screen.parent = self
        self.focus.add_client(screen)
        self.logger.info(f"Add screen({screen.id})")


    def addAction(self,key: str | int,callable: Callable): # type: ignore

        if isinstance(key,str):
            if len(key) != 1:
                raise Exception(f"addKeyAction, key length is {len(key)}")
            key = ord(key)
        
        self.logger.info(f"Adding key {key}")
        self.global_actions[key] = callable


    def handleKey(self,c):

        if c in self.global_actions:
            self.logger.debug("Doign global action screenhandler")
            self.global_actions[c]()
            return

        if self.focus.spotlight != None:
            self.focus.spotlight.handleKey(c)
            return

        self.logger.debug(f" Spotlight is None in handleKey")



'''
Glossary
Focusable: means that it can receive focus and be the only thing that can receive input at the moment (Unless global keys intercept it)
Global focus: When there are no focused items, global key listening is present (good for menus?)
'''



'''
Screen holds layout components
'''


class Screen(RenderAttributes,FocusableClient):

    terminal_window:curses.window #stdsrc

    def __init__(self,**kwargs:Unpack[ScreenType]) -> None:
        term_lines,term_cols = Screen.terminal_window.getmaxyx() 


        color_level = 1
        kwargs.setdefault("color_level",1)
        kwargs.setdefault("default_background",defaultcolors.NORMAL)

        self.window = curses.newwin(term_lines,term_cols,0,0)

        
        # self.background = kwargs.pop("background",None)
        self.visible = False
        self.layouts:list[Layout]  = []
        

        


        super().__init__(**kwargs)
        self.focus = FocusManager(self.class_name,self.id)

        self.logger.debug(f"SHak background is {self.background}")
        

    def get_screen_size(self):
        return self.window.getmaxyx()

        
    def get_window(self):
        return self.window


    def defaultHandleGetFocus(self, direction: Direction):

        # self.render_attributes_default_get_focus(self.window)
        self.visible = True
        self.show()



    def defaultHandleLoseFocus(self, direction: Direction):

        # self.render_attributes_default_get_focus(self.window)
        self.visible = False
        self.window.clear()
        self.window.refresh()



    #TODO check that it is layout
    def add_layout(self, layout:"Layout"):

        if not isinstance(layout,Layout):
            raise Exception(f"Error: {layout} is not a layout")



        self.logger.info("Adding layout")
        layout.screen = self
        layout.parent = self
        self.layouts.append(layout)

        #TODO allow decoration layouts
        
        if isinstance(layout,FocusableClient):
            self.logger.info("Adding Focusable Layout")
            self.focus.add_client(layout)
            layout.focus.focus_parent = self.focus



    def show(self):
        """
        Renders each layout
        Makes the layout spotlight handle_receiving_focus
        """

        self.logger.info(f"Screen is about to show")

        for layout in self.layouts:
            layout.show()


        if self.background != None:
            self.window.bkgd(" ",self.background)



        self.focus.set_spotlight_first(Direction.SCREEN_JUMP)
        self.window.refresh()



    def handleKey(self,c):

        if self.focus.spotlight != None:
            self.focus.spotlight.handleKey(c)
            return

        raise Exception(f"class Screen; Func [handleKey] does not have a layout in spotlight\nWeird a layout should have at least a layout")



class FocusableLayout(Layout,FocusableClient):
    """
    Can contain FocusableItem and DecorationItem
    Spotlight can only be FocusableItem
    """ 

    def __init__(self, **kwargs:Unpack[LayoutType]) -> None:
        super().__init__(**kwargs)
        self.focus = FocusManager(self.class_name,self.id)
        

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
        """
        When a layout gains focus from Forward or Backwards, the first or last item gain focus.
        """

        #TODO fix Direction.JUMP and Direction.SCREEN_JUMP they are weird , maybe remove Screen_JUMP

        super().handle_receive_focus(direction)


        if direction == Direction.FORWARD or direction == Direction.SCREEN_JUMP:
            self.focus.set_spotlight_first(direction)

        if direction == Direction.BACKWARD:
            self.focus.set_spotlight_last(direction)

        if direction == Direction.JUMP:
            self.focus.tell_current_client_gain_focus(direction)


    def defaultHandleLoseFocus(self, direction: Direction):
        super().handle_lose_focus(direction)
        self.focus.tell_current_client_lose_focus(direction)


class GlobalKeyLayout(Layout,FocusableClient):
    """
    Can contain GlobalKeyItem and DecorationItem
    """ 


    def __init__(self, **kwargs:Unpack[LayoutType]) -> None:
        super().__init__(**kwargs)
        
        self.focus = FocusManager(self.class_name,self.id)


    def handleKey(self,c):

        if c in self.registered_global_keys:
            self.registered_global_keys[c]()
            return



        if c == ord("\t") or c == curses.KEY_BTAB:
            direction = Direction.FORWARD if c == ord("\t") else Direction.BACKWARD 
            if self.focus.focus_parent != None:
                self.focus.focus_parent.move(direction)
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



#TODO implement it
class DecorationLayout(Layout):
    """
    Layout that is not focusable , which means it cannot handle keys
    """
    def __init__(self, **kwargs: Unpack[LayoutType]) -> None:
        super().__init__(**kwargs)
    pass

    def validate_item(self, item: "Item") -> Tuple[bool, None | Exception]:
        return True,None


class DecorationItem(Item):
    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)

    

class GlobalKeyItem(Item):
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

        kwargs.setdefault('cols',self.length)
        kwargs.setdefault('lines',1)
        super().__init__(**kwargs)


    def paint(self):


        self.paint_normal_state(self.window)
        self.insert_text(self.text)



class ButtonBase(Item):
    def __init__(self,text,**kwargs) -> None:
        self.length = len(text)
        self.text = text

        self.actions:list[Callable] = []

        super().__init__(**kwargs)
        
    def paint(self):

        self.paint_normal_state(self.window)
        self.insert_text(self.text)


    def getWin(self):
        return self.window

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


        self.render_attributes_default_get_focus(self.window)
        self.logger.info("Receiving focus")
        

    def defaultHandleLoseFocus(self,direction:Direction):

        self.render_attributes_default_lose_focus(self.window)
        self.logger.info("Loosing focus")


    def handleKey(self, c):

        if c in self.actions:
            self.actions[c]()

        self.logger.info(f"Buttonfocusable handling key {c}")
        





#TODO fix rendering, without a border it seems to crash
class Input(Item,FocusableClient):
    def __init__(self,**kwargs:Unpack[ItemAttributesType]) -> None:

        min_width = kwargs.setdefault('min_width',10)

        self.filter = None
        self.length = kwargs.get('min_width')
        self.cursorx = -1 if not kwargs.get('hasBorder') else 0
        self.cursory = 0 if not kwargs.get('hasBorder') else 1
        self.max_line,self.max_col = -1,-1

        
        kwargs.setdefault('lines',1)
        kwargs.setdefault('cols',min_width)


        super().__init__(**kwargs)


    def defaultHandleGetFocus(self,direction:Direction):

        self.window.move(self.cursory,self.cursorx)
        self.render_attributes_default_get_focus(self.window)
        self.logger.info("Receiving focus")

    def defaultHandleLoseFocus(self,direction:Direction):

        self.render_attributes_default_lose_focus(self.window)
        self.logger.info("Loosing focus")




    def paint(self):
        self.paint_normal_state(self.window)

        self.max_line,self.max_col = self.window.getmaxyx()
        self.logger.info(f"info max_col es {self.max_col}")


    def getWin(self):
        return self.window

    def backspace(self):

        if self.hasBorder:
            if self.cursorx <= 0:
                return

        if self.cursorx < 0:
            return
        
        

        self.window.move(self.cursory,self.cursorx)
        self.window.addch(" ")
        self.window.move(self.cursory,self.cursorx)
        self.cursorx += -1

        self.text.pop(-1)
        
        self.window.refresh()
        return

    def should_skip(self,c):
        if self.filter != None:
            should_allow_key = self.filter(c)

            if should_allow_key == False:
                return True

            elif should_allow_key:
                return False

            else:
                raise Exception(f"Error in Input self.filter, it should return boolean but returned {type(should_allow_key)}")

    def handleKey(self,c):
        self.logger.info(f"handling key in input {c}")


        if c == curses.KEY_ENTER or c == ord("\n"):
            return
        
        if c == curses.KEY_BACKSPACE:
            self.backspace()
            return

        if c == curses.KEY_LEFT or c == curses.KEY_RIGHT:
            return

        if self.should_skip(c):
            return





        self.cursorx += 1

        #Make sure cursor does not overlap with border
        if self.hasBorder:
            if self.cursorx >= self.max_col-2:
                self.cursorx  = self.max_col -3
                return

        
        #Make sure not surpass max_col
        if self.cursorx >= self.max_col-1:
            self.cursorx  = self.max_col -2
            return

        self.window.move(self.cursory,self.cursorx)
        self.window.addch(self.cursory,self.cursorx,c)
        
        self.window.refresh()






if __name__ == "__main__":
    print(ButtonGlobalKey.mro())
