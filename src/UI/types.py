from typing import TypedDict,Required,Literal
from UI.colors import Color
from UI.properties import Where,Padding,Push

__all__ = ["Coordinates"]


class Coordinates(TypedDict):
    topx:int
    topy:int


class BaseType(TypedDict,total=False):
    id:str | None


class RenderAttributesType(TypedDict,total=False):
     push:Push
     padding:Padding
     hasBorder:bool
     background:int | None | Color
     background_focus:int | None | Color
     character_color:int | None  | Color
     min_width:int
     max_width:int


class LayoutType(RenderAttributesType,BaseType,total=False):
    coordinates:Coordinates | None
    where:Where | None
    axis:Literal["horizontal","vertical"]


class ItemAttributesType(RenderAttributesType,BaseType,total=False):
     lines:int
     cols:int


class InputType(ItemAttributesType,total=False):
    hide_characters:bool


class ScreenType(BaseType,total=False):
    background:int | None




class ButtonBaseType(ItemAttributesType):
     text:Required[str]


class ButtonGlobalKeyType(ButtonBaseType,total=False):
     text:Required[str]
     global_key_char:Required[str]
     global_key:int
