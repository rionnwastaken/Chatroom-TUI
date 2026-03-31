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

from ui import ButtonFocusable,ButtonGlobalKey, Item,Screen,ScreenHandler,Layout,ReusableActions,Label,Input,Where,Padding,Push

import ui


logger = logging.getLogger()
logging.basicConfig(filename='window.log', level=logging.INFO)

with open("./window.log","w") as f:
    f.write("")



ui.logger = logger





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
        curses.init_pair(6, 200, 100)


        logger.info(f"COlors are : ?{ curses.COLOR_WHITE,curses.COLOR_BLUE }")

    

    def coloring(self,stdsrc:curses.window):


        for i in range(1, 254):
            curses.init_pair(i, curses.COLOR_WHITE, i)

        max_lines, max_cols = stdsrc.getmaxyx()
        x, y = 0, 0
        color = 1

        size =2

        while color < 254:
            # Check if we've run out of vertical space
            if y >= max_lines:
                break

            # Wrap to next line
            if x >= max_cols:
                y += 1
                x = 0
                if y >= max_lines: break

            # Draw directly to stdsrc instead of creating a window
            try:
                # attron sets the color for the next character added
                stdsrc.attron(curses.color_pair(color))
                stdsrc.addch(y, x, 'c')
                stdsrc.attroff(curses.color_pair(color))
            except curses.error:
                # This handles the bottom-right corner edge case
                pass

            color += 1
            x += 1

        stdsrc.refresh()

        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue






    def main(self, stdsrc:curses.window):
        self.init_colors()
        stdsrc.timeout(100)
        curses.mousemask(curses.BUTTON1_CLICKED)
        curses.mouseinterval(0)
        stdsrc.refresh()


        self.coloring(stdsrc)


        max_win_height,max_win_width = 3,10
        virt_offset_width = 10
        virt_offset_height = 2
        pad = curses.newpad(
            max_win_height + virt_offset_height,
            max_win_width + virt_offset_width
        )
        max_virt_height,max_virt_width = pad.getmaxyx()


        winx =-1 
        virtx =-1 
        virty = 0
        viewx,viewy = 0,0 #View moves whenever i get to the edge and want to move further

        default_border = 2


        wrappery,wrapperx =3,10

        # +1  to end up inside the border
        topy,topx = wrappery + 1, wrapperx + 1

        #substract -1 we start counting at 0 to make it fit inside border
        bottomy,bottomx = topy + max_win_height -1  , topx + max_win_width -1
        data = []


        wrapper = curses.newwin(
            max_win_height + default_border,
            max_win_width + default_border,
            wrappery  ,
            wrapperx  ,
        )
        wrapper.border()
        wrapper.bkgd(" ",curses.color_pair(6))
        wrapper.refresh()



        #View should only move whenever i am at the edge and i should only be able to move in the positions of the array
        


        def update():
            pad.refresh(
                viewy,
                viewx,
                topy,
                topx,
                bottomy,
                bottomx
            )

        def erase():
            nonlocal winx,viewx,virtx

            if len(data) <= 0:
                logger.info("\t erase there is no data")
                return

            pad.delch()
            data.pop(-1)
            move('backward')


        def move_view_if_needed(dir:Literal['forward','backward']):
            nonlocal winx,viewx,virtx

            # Cannot move view more if we at the limit of  virtual width?


            if dir == 'forward':

                if virtx >= max_virt_width:
                    return

              #right edge
                if winx >= max_win_width:
                    winx = max_win_width
                    viewx += 1


            if dir == 'backward':


                if virtx < 0:
                    logger.info(f"virtx {virtx} in 'backward'")
                    return

                #left edge
                if winx <= 0:
                    winx = 0
                    viewx += -1

                if viewx < 0:
                    viewx = 0

        def is_outside_data_boundary():
            nonlocal virtx,viewx,winx

            if virtx >= len(data):
                return True

            return False


        def move(dir:Literal['forward','backward']):
            nonlocal virtx,viewx,winx

            force = 1 if dir == 'forward' else -1
            virtx += force
            winx += force

            should_move = False


            if is_virtx_outside_upper_boundary():
                logger.info(f"virt outside upper boundary {virtx,max_virt_width}")
                virtx = max_virt_width-1
                winx = max_win_width-1

            elif is_outside_data_boundary() and dir == 'forward':
                logger.info(f"virt outside data boundary {virtx,len(data)}")
                virtx += ( force * -1 )
                winx += ( force * -1 )


            elif is_virtx_outside_lower_boundary():
                logger.info(f"virt outside lower boundary {virtx}")
                virtx = -1
                winx = -1

            else:
                should_move = True

            if should_move:
                pad.move(virty,virtx)

            move_view_if_needed(dir)
            update()



        def is_virtx_outside_upper_boundary():

            if virtx >= max_virt_width:
                return True
            return False

        def is_virtx_outside_lower_boundary():

            if virtx <= -1:
                return True
            return False

            


        def add(c):
            nonlocal viewy,viewx,virtx,winx

            # if virtx + 1 > len(data) -1:
            #     return


            virtx += 1
            winx += 1

            if is_virtx_outside_upper_boundary():
                virtx = max_virt_width -1 
                winx = max_win_width -1
                return



            data.append(c)
            pad.insch(virty,virtx,c)
            move_view_if_needed('forward')
            # pad.move(0,virtx)
            update()





        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue

            logger.info(f"virtx {virtx}")

            if c == curses.KEY_LEFT:
                move('backward')

            elif c == curses.KEY_RIGHT:
                move('forward')

            elif c == curses.KEY_BACKSPACE:
                erase()
                pass

            else:
                add(c)


            logger.info(f"Current::\t virtx {virtx} winx {winx} viewx {viewx}")


    





        screen_handler = ScreenHandler(stdsrc)
        reusable_actions = ReusableActions(screen_handler)







        scr = Screen("a")
        lay = Layout(focusable=True,where=Where.CENTER_OF_SCREEN)
        btn = ButtonGlobalKey(text="hey",global_key_char='a',background=3)
        btn_f = ButtonGlobalKey(text="hey",global_key_char='b',background=3)
        label  = Label("hello")


        btn.addAction(ReusableActions.changeColor(btn))
        btn_f.addAction(ReusableActions.changeColor(btn_f))
        # btn2 = ButtonFocusable("hey")


        lay.add_item(btn)
        lay.add_item(btn_f)
        lay.add_item(label)
        scr.add_layout(lay)


        lay2 = Layout(focusable=True,coordinates={"topx":10,"topy":15})
        input = Input(hasBorder=True)
        input2 = Input(hasBorder=True)
        btn_focus = ButtonFocusable(text="hello",background=2,hasBorder=True)
        something = ButtonFocusable(text="View messages (A) Send messages (B) Join Chat(C)",background=2,hasBorder=True)

        def f(key,message):
            key = ord(key)

            def fi():
                logger.info(message)
            something.addAction(key,fi)


        f('A',"Pressed A")
        f('B',"Pressed B")
        f('C',"Pressed C")

        
        def tr(item:Item):

            def i():
                item.layout_api.traverse('forward')

            return i


        btn_focus.addAction(curses.KEY_RIGHT,tr(btn_focus))





        btn_focus.addAction('\n',ReusableActions.changeColor(btn_focus))
        btn_focus.on_receive_focus = ReusableActions.changeColor2(btn_focus, 3)


        lay2.add_item(btn_focus)
        
        logger.info(f"Layout traversal index before adding {lay2.traversal_index}")

        lay2.add_item(input)
        lay2.add_item(input2)
        lay2.add_item(something)

        lay2.set_spotlight(input)


        scr.add_layout(lay2)
        screen_handler.add_screen(scr)


        logger.info(f"Layout traversal  index after adding {lay2.traversal_index}")


        scr.set_spotlight(lay2)

        stdsrc.keypad(True)
        





        while (True):

            c = stdsrc.getch()
            if c == -1:
                continue


            if c == curses.KEY_RESIZE:
                screen_handler.draw()
                logger.info(f"NEW SIZE {stdsrc.getmaxyx()}")


            # logger.info(f"key {c}")

            screen_handler.handleKey(c)

            # screen_login.show()

            pass

#test

Main()




