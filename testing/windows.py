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

from gui import ButtonFocusable,ButtonGlobalKey,Screen,ScreenHandler,Layout,ReusableActions,Label,Input,Where,Padding,Push
import gui



logger = logging.getLogger()
logging.basicConfig(filename='window.log', level=logging.INFO)

with open("./window.log","w") as f:
    f.write("")



gui.logger = logger





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

        


        # screen = Screen(screen_name_identifier="i")
        # layout =  Layout(focusable=True,axis="vertical",where=Where.CENTER_OF_SCREEN)
        #
        # input_name = Input(hasBorder=True,min_width=10,background=2)
        # label =  Label("Nombre:")
        #
        # layout.add_item(label)
        # layout.add_item(input_name)
        # input_lastname = Input(hasBorder=True,min_width=10,background=2)
        # label =  Label("Last Name:")
        #
        # layout.add_item(label)
        # layout.add_item(input_lastname)
        #
        #
        #
        # layout_gords =  Layout(focusable=True,axis="horizontal",coordinates={"topx":50,"topy":5})
        # input_gorditas = Input(hasBorder=True,min_width=10,background=2)
        # label =  Label("Nombre:")
        #
        # layout_gords.add_item(label)
        # layout_gords.add_item(input_gorditas)
        # input_chetos = Input(hasBorder=True,min_width=10,background=2)
        # label =  Label("Last Name:")
        #
        # layout_gords.add_item(label)
        # layout_gords.add_item(input_chetos)






        # screen.add_layout(layout_gords)
        # screen.add_layout(layout)
        # screen_handler.add_screen(screen)





        scr = Screen("a")
        lay = Layout(focusable=True,global_keys=True,where=Where.CENTER_OF_SCREEN)
        btn = ButtonGlobalKey("hey",'a',background=3)

        btn.addAction(ReusableActions.changeColor(btn))
        # btn2 = ButtonFocusable("hey")


        lay.add_item(btn)
        scr.add_layout(lay)

        screen_handler.add_screen(scr)

        
        logger.info(ButtonGlobalKey.mro())





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




