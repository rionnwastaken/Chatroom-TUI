import logging
import curses
from typing import Unpack

from UI.colors import Color
from UI.types import RenderAttributesType


logger = logging.getLogger()


class RenderAttributes():

    def __init__(self,**kwargs:Unpack[RenderAttributesType]) -> None:
        self.lines = kwargs.pop('lines', None)
        self.cols = kwargs.pop('cols', None)
        self.push  = kwargs.pop('push',None)
        self.padding  = kwargs.pop('padding', None)
        self.hasBorder = kwargs.pop('hasBorder',None,)
        self.background = kwargs.pop('background',None,)
        self.background_focus = kwargs.pop('background_focus',None)
        self.character_color = kwargs.pop('character_color',None)
        self.min_width = kwargs.pop('min_width',None,)
        self.max_width = kwargs.pop('max_width',None,)

        self._default_background = kwargs.pop('default_background',None,)
        self._default_background_focus = kwargs.pop('default_background_focus',None,)
        self._color_level = kwargs.pop('color_level',None,)

        
        self.is_rendered = False # Flag that is True whenwe show the screen

        if self.background == None:
            self.background = self._default_background

        if self.background_focus == None:
            self.background_focus = self._default_background_focus

        if isinstance(self.background,Color):
            self.background = self.background * self._color_level


        if isinstance(self.background_focus,Color):
            self.background_focus = self.background_focus * self._color_level

        
        self.window:curses.window
        super().__init__(**kwargs)



    
    def paint_normal_state(self,win):
        if self.hasBorder:
            self.window.box()


        self.window.bkgd(" ",self.background)
        self.window.refresh()

    def render_attributes_default_get_focus(self,win):
        if self.hasBorder:
            self.window.box()

        
        self.window.bkgd(" ",self.background_focus)
        self.window.refresh()


    def render_attributes_default_lose_focus(self,win):
        self.paint_normal_state(self.window)


    def set_correct_background_value(self):

        if isinstance(self.background,Color):
            self.background = self.background * self._color_level
            return


    def get_color_pair_level(self,classes:list[tuple[type,int]],clazz_to_compare:object):

        for obj in classes:
            clazz = obj[0]
            if isinstance(clazz_to_compare,clazz):
                return obj[1]


class DefaultAttrbutes(RenderAttributes):
    def __init__(self, **kwargs: Unpack[RenderAttributesType]) -> None:
        super().__init__(**kwargs)


    def set_default_attributes(self,kwargs:RenderAttributesType):
        """Only set default  attributes is None"""

        if  kwargs.get("background") == None:
            kwargs['background'] = self.background


        if  kwargs.get("background_focus") == None:
            kwargs["background_focus"] = self.background_focus

        if  kwargs.get("character_color") == None:
            kwargs["character_color"] = self.character_color

        if  kwargs.get("hasBorder") == None:
            kwargs["hasBorder"] = self.hasBorder

        if  kwargs.get("padding") == None:
            kwargs["padding"] = self.padding


        if  kwargs.get("push") == None:
            kwargs["push"] = self.push


        logger.info("Printing kwargs")
        logger.info(str(kwargs))

        return kwargs

    def merge(self,other:"DefaultAttrbutes"):
        if other.background != None:
            self.background = other.background

        if other.background_focus != None:
            self.background_focus = other.background_focus

        if other.background_focus != None:
            self.background_focus = other.background_focus


        if  other.character_color != None:
            self.character_color = other.character_color

        if  other.hasBorder != None:
            self.hasBorder = other.hasBorder

        if  other.padding != None:
            self.padding = other.padding


        if  other.push != None:
            self.push = other.push







class DefaultAttributeManager:

    instances:dict[object,DefaultAttrbutes] = {}


    @staticmethod
    def init_default_attrs(clazz:object,defaultAttributes:DefaultAttrbutes):
        if DefaultAttributeManager.instances.get(clazz,None):
            instance = DefaultAttributeManager.instances.get(clazz)
            assert instance != None
            instance.merge(defaultAttributes)
        else:
            DefaultAttributeManager.instances[clazz] = defaultAttributes

    @staticmethod
    def set(clazz:object,kwargs):
        if not DefaultAttributeManager.instances.get(clazz,None):
            raise Exception(f"Error: Must call init before set, class {clazz}")

        default_attributes = DefaultAttributeManager.instances[clazz]
        default_attributes.set_default_attributes(kwargs)
