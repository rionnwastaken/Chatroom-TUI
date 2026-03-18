from curses import wrapper
import curses

from curses.textpad import Textbox, rectangle

import logging
from os import linesep

logger = logging.getLogger('')
logging.basicConfig(filename='myapp.log', level=logging.INFO)


def info(message):
    logger.info(message)



def keyc(_key:str):
    return ord(_key)

class Master():
    def __init__(self) -> None:
        self.max_length = 40
        self.x_pos = 0
        self.y_pos = 0
        self.write_first_char_insert = False

        self.rows = ["Name:","Last name:","Age:","Gender:"]
        self.rows_startpos = [len(i) for i in self.rows]
        self.rows_content = [[] for _ in self.rows]



        wrapper(self.main)

    def get_realpos_x(self):
        return self.x_pos - self.rows_startpos[self.y_pos]

    def move(self,dir_y=None,dir_x=None):

        def downward(dir_y):
            is_downward = dir_y > 0
            if is_downward:

                if self.y_pos == len(self.rows)-1:
                    return

                self.y_pos += 1
                self.x_pos = self.rows_startpos[self.y_pos] + len(self.curr_line())
                self.stdscr.move(self.y_pos,self.x_pos)
                return

            if self.y_pos > 0:
                self.y_pos += -1
                # self.x_pos = self.rows_startpos[self.y_pos]
                self.x_pos = self.rows_startpos[self.y_pos] + len(self.curr_line())
                self.stdscr.move(self.y_pos,self.x_pos)
                return

            

        def sideways(
            dir_x,
        ):

            self.write_first_char_insert = False
            is_forward = dir_x > 0
            if is_forward:

                realx = self.get_realpos_x()
                if realx < len(self.curr_line()):
                    self.x_pos += 1
                    self.stdscr.move(self.y_pos,self.x_pos)
                    # info(f"forw Postmove x={self.x_pos} r={self.get_realpos_x()}")

                return


            if self.x_pos > self.rows_startpos[self.y_pos]:
                self.x_pos -= 1
                self.stdscr.move(self.y_pos,self.x_pos)
                # info(f"backw Postmove x={self.x_pos} r={self.get_realpos_x()}")
                # self.stdscr.addstr("|")


        if dir_y != None:
            downward(dir_y)
            return

        if dir_x != None:
            sideways(dir_x)








        

    def curr_line(self):
        return self.rows_content[self.y_pos]


    def write(self,key):

        realx = self.get_realpos_x()
        if len(self.curr_line()) >= self.max_length:
            pass
        else:

            if realx < len(self.curr_line()):

                if self.write_first_char_insert:
                    self.x_pos += 1
                    self.stdscr.move(self.y_pos,self.x_pos)

                # info(f"[preinsert] length=[{len(self.curr_line())}] x_pos={self.x_pos} realx={self.get_realpos_x()}")
                self.curr_line().insert(realx,key)
                self.stdscr.insnstr(key,len(key))

                if not self.write_first_char_insert:
                            self.write_first_char_insert = True
                            # self.x_pos += 1
                            # self.stdscr.move(self.y_pos,self.x_pos)


                info(f"[post] length=[{len(self.curr_line())}] x_pos={self.x_pos} realx={self.get_realpos_x()}")
                return



            self.rows_content[self.y_pos].append(key)
            self.stdscr.move(self.y_pos,self.x_pos)
            self.stdscr.addch(key)
            self.x_pos += 1
            
    def backspace(self):
        if self.x_pos > self.rows_startpos[self.y_pos]:
            self.x_pos -= 1
            self.stdscr.move(self.y_pos,self.x_pos)
            self.stdscr.delch()
            realx = self.get_realpos_x()
            del self.curr_line()[realx]
        pass


    def create_window(self) -> curses.window:
        begin_x = 20; begin_y = 0
        height = 50; width = 400
        win:curses.window = curses.newwin(height, width, begin_y, begin_x)
        win.box()
        win.addstr(1,1,"hello brub")
        return win

    def create_pad(self):
        pad = curses.newpad(100, 100)
# These loops fill the pad with letters; addch() is
# explained in the next section
        for y in range(0, 99):
            for x in range(0, 99):
                pad.addch(y,x, ord('a') + (x*x+y*y) % 26)

# Displays a section of the pad in the middle of the screen.
# (0,0) : coordinate of upper-left corner of pad area to display.
# (5,5) : coordinate of upper-left corner of window area to be filled
#         with pad content.
# (20, 75) : coordinate of lower-right corner of window area to be
#          : filled with pad content.
        pad.refresh( 0,0, 5,5, 20,75)
                


    def main(self,stdscr:curses.window):
        self.stdscr:curses.window = stdscr
        # print(curses.erasechar())
        if curses.curs_set(1) == curses.ERR:
            stdscr.addstr("Cannot set cursor to normal visibility\n")
            exit(0)


        
        # Clear screen
        stdscr.clear()
        curses.start_color()

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_WHITE)





        for index,row in enumerate(self.rows,0):
            stdscr.addstr(index,0,row)
        self.y_pos,self.x_pos = 0,len( self.rows[0] )

        stdscr.move(self.y_pos,self.x_pos)
        curses.noecho()
        curses.cbreak()
        # curses.nl()

        self.stdscr.refresh()
        self.win = self.create_window()
        self.win.refresh()

        while True:
            try:

                return_value = self.keyHandle()

                if return_value != None:
                    if type(return_value) == str:

                        if return_value == "exit":
                            curses.endwin()
                            break

                stdscr.refresh()
            except:
                pass

    def keyHandle(self):

        # key = self.stdscr.getkey()
        key = self.stdscr.getch()
        # info(key)


        if key ==  -1:
            return "exit"


        if key == curses.KEY_RIGHT:
            self.move(dir_x=1)
            return
        if key == curses.KEY_LEFT:
            self.move(dir_x=-1)
            return
        if key == curses.KEY_UP:
            self.move(dir_y=-1)
            return
        if key == curses.KEY_DOWN:
            self.move(dir_y=1)
            return

        if key == curses.KEY_BACKSPACE:
            self.backspace()
            return
        if key == keyc( '\t' ):
            self.move(dir_y=1)
            return

        # if (key == keyc("q")):
        #     return "exit"
            
        self.write(chr(key))


master = Master()
