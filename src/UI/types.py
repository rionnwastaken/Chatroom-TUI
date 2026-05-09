from typing import TypedDict,Required,Literal
from UI.properties import Where,Padding,Push

__all__ = ["Coordinates"]


class Coordinates(TypedDict):
    topx:int
    topy:int


class FocusableClientType(TypedDict,total=False):
    id:str | None


class LayoutType(FocusableClientType,total=False):
    coordinates:Coordinates | None
    where:Where | None
    hasBorder:bool
    background:int
    axis:Literal["horizontal","vertical"]
    padding:Padding
    push:Push


class ItemAttributesType(FocusableClientType,total=False):
     push:Push
     padding:Padding
     hasBorder:bool
     background:int | None
     lines:int
     cols:int
     min_width:int
     max_width:int


class ScreenType(FocusableClientType,total=False):
    background:int | None




class ButtonBaseType(ItemAttributesType):
     text:Required[str]


class ButtonGlobalKeyType(ButtonBaseType,total=False):
     text:Required[str]
     global_key_char:Required[str]
     global_key:int
