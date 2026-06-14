import curses
from typing import Callable, Dict,Tuple,Unpack
from abc import ABC, abstractmethod
import logging

from UI.attributes import DefaultAttributeManager, RenderAttributes
from UI.properties import Where,Padding,Push,Direction
from UI.properties import Where,Padding,Push,Direction
from UI.types import LayoutType,ItemAttributesType
from UI.types import RenderAttributesType
from UI.utils import CustomAdapter,root_logger_name
from UI.colors import Color, DefaultColors

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from UI.ui import Screen,Layout,Item

root = logging.getLogger(root_logger_name)
logger = CustomAdapter(root)


defaultcolors = DefaultColors.get_instance()


class Base(ABC):
    def __init__(self,**kwargs) -> None:


        self.id:object = kwargs.pop("id",None) 
        self.class_name = self.__class__.__name__
        self.full_name = self._create_full_name()
        self.parent:None | object = None


        self.logger = CustomAdapter(root,{"class_full_name":self.full_name})

        self.logger.debug(f"I am {type(self)}")


        super().__init__(**kwargs)


    def _create_full_name(self):



        name = f"{self.class_name}"
        if self.id != None:
            name += f"({self.id})"

        return name















class Layout(RenderAttributes,Base,ABC):
    ''' 
    A layout is a window that holds items
    It calculates the  required dimensions to fit the items
    Parent of FocusableLayout and GlobalKeyLayout
    Layout creates the derevied windows for the Items
    '''


    def __init__(self, **kwargs:Unpack[LayoutType]) -> None:


        color_level = 2

        kwargs.setdefault("color_level",color_level)
        DefaultAttributeManager.set(Layout,kwargs)
        kwargs.setdefault("color_level",Layout.color_level)



        self.items:list["Item"] = [] 
        self.is_rendered = False
        self.screen:Screen
        self.registered_global_keys:Dict[int,Callable] = {}



        #RENDERING ATTRIBUTES

        self.axis = kwargs.pop('axis','horizontal')

        self.total_width = 0 
        self.total_height = 0

        self.item_current_posx = 0
        self.item_current_posy = 0

        self.where = kwargs.pop('where',None)
        self.coordinates = kwargs.pop('coordinates',None)

        if self.coordinates != None:
            self.topx = self.coordinates["topx"]
            self.topy = self.coordinates["topy"]

        if self.where == None and self.coordinates == None:
            raise Exception("Currently it is not supported to automatically position a layout without coordinates or where   ")


        if self.where != None and self.coordinates != None:
            raise Exception("Cannot use where and coordinates at the same time")



        self.default_border_padding = 2






        super().__init__(**kwargs)





        




    def _create_layout_window(self) -> curses.window:

        layout_height = 0
        layout_width = 0

        biggerst_height = 0
        biggest_width = 0

        for item in self.items:
            item_lines,item_cols = item.get_total_space()

            if item.hasBorder:
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



        win = self.screen.get_window()
        maxY,maxX = win.getmaxyx()

        if (self.total_height + topy) >= maxY:
            #TODO fix what happens when layout window exceeds the limits of the termial window, should terminal window be a pad? or no
            raise Exception("Dont worry, be happy")

        self.logger.debug(f"Deriving window heigth widh topy topx {self.total_height} {self.total_width} {topy} {topx} {self.screen.get_window()}")
        self.window = self.screen.get_window().derwin(
            self.total_height,
            self.total_width,
            topy,
            topx
        )

        self.logger.debug("Deriving window finnished")
        self.logger.debug(f"layout_window size {self.window.getmaxyx()}")


        return self.window

    def paint_layout(self):

        if self.hasBorder:
            self.window.box()


        # if self.background == None:
        #     self.logger.debug(f"Layout setting default background {defaultcolors.NORMAL * 1}")
        #     self.window.bkgd(" ",defaultcolors.NORMAL * 1 )
        #
        # else:
        self.logger.debug(f"Layout setting background {self.background}")
        self.window.bkgd(" ",self.background)


        self.window.noutrefresh()


    def show(self):
        """
        Paints itself and the items
        """
        if not self.is_rendered:
            self.is_rendered = True
            self.render()


        self.paint_layout()
        for item in self.items:
            item.paint_item()
            item.is_rendered = True

        curses.doupdate()
        


    #TODO make it easier to work with, maybe functionalize steps
    def render(self):

        self.logger.info(f"{'-'*10}RENDERING LAYOUT{'-'*10}")

        self.total_width = 0
        self.total_height = 0

        self.item_current_posx = 0
        self.item_current_posy = 0

        if len(self.items) <=0:
            self.logger.debug("Layout has no items in screen")
            self.window = self._create_layout_window()
            return


        self.window = self._create_layout_window()
        self.paint_layout()

        if self.window == None:
            raise Exception("Layout window is null")


        #Create subwins
        for item in self.items:
            width = item.cols
            height = item.lines
            margin = item.push
            padding = item.padding

            border = self.default_border_padding if item.hasBorder else 0

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

                

            a  = self.window.getmaxyx()
            self.logger.debug(f"menuwin lines={a[0]} cols={a[1]}")
            self.logger.debug(f"itemwin lines={win_lines} cols={win_cols} posy={self.item_current_posy} posx={self.item_current_posx} ")

            item_win:curses.window = self.window.derwin(
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
                

            item.parent = self
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
        self.render_attributes_default_get_focus(self.window)
        self.logger.debug("Layout receive focus")


    def handle_lose_focus(self,from_where:Direction):
        """ Can be overriden to hook more functionality """
        self.render_attributes_default_lose_focus(self.window)
        self.logger.debug("Layout  losing focus")



    def hide(self):
        self.window.clear()
        self.window.refresh()

'''
Item can hold anything, it only cares about its dimensions 
Item is widget holder for example for labels ,inputs
'''
class Item(RenderAttributes,Base,ABC):

    def __init__(
        self,
        **kwargs:Unpack[ItemAttributesType]
    ) -> None:


        kwargs.setdefault("color_level",Item.color_level)
        DefaultAttributeManager.set(Item,kwargs)
        kwargs.setdefault("default_background",defaultcolors.NORMAL_PURPLE * color_level)

        
        self.layout_api:Layout

        super().__init__(**kwargs)

        
        



    def set_win(self,win:curses.window):
        self.window = win

    def get_total_space(self) -> tuple[int,int]:
        self.logger.info(f"self.lines is {self.lines}")
        lines = self.lines + self.push.bottom + self.push.top +  self.padding.top + self.padding.bottom
        cols = self.cols + self.push.right + self.push.left + self.padding.right + self.padding.left

        return (lines,cols)

    
    


    def insert_text(self,text):

        if not self.hasBorder:
            self.window.insstr(0,0,text)
        else:
            self.window.addstr(1,1,text)



    def paint_item(self):
        self.clear()
        self.paint()
        self.window.noutrefresh()

    @abstractmethod
    def paint(self):
        raise NotImplementedError()

    def show(self):
        self.logger.info("Showing item")
        self.paint()
        

    def clear(self):
        self.window.clear()
        self.window.noutrefresh()
