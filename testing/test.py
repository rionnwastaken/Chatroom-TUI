import curses
import logging


logger = logging.getLogger('')
logging.basicConfig(filename='test.txt', level=logging.INFO)

        
class Operations():
    def __init__(self,stdscr,box:"Box") -> None:
        self.stdscr:curses.window = stdscr
        self.box = box

        self.end_pad_col = box.end_pad_col
        self.end_win_col = box.end_win_col

        self.row_size = box.row_size
        self.column_size = box.column_size
        self.x_pos = 0
        self.y_pos = 0 

        self.pcol = 0
        self.grid = [[]]

        pass


    def refresh(self):
        self.stdscr.refresh(0,self.pcol,*self.box.wt,*self.box.wb)

    def scroll_if_reach_border(self):
        if self.x_pos > self.end_pad_col:
            self.pcol = 0
            self.x_pos = 0
            

            self.y_pos += 1
            self.addlineif()

        if self.x_pos >= self.end_win_col:
            self.pcol += 1

    def curr_line(self):
        return self.grid[self.y_pos]

    def addlineif(self):
        if self.y_pos >= len(self.grid):
            self.grid.append([])

    def put(self,c):

        self.scroll_if_reach_border()
        self.stdscr.addch(c)
        self.curr_line().append(c)
        self.x_pos += 1
    def move(self,dir_y=None,dir_x=None):

        # def downward(dir_y):
        #     is_downward = dir_y > 0
        #
        #     if is_downward:
        #         self.stdscr.move(self.y_pos,self.x_pos)
        #         return
        #
        #     self.stdscr.move(self.y_pos,self.x_pos)
        #     return

            
        def sideways(dir_x):

            is_forward = dir_x > 0
            if is_forward:
                logger.info(f"{self.x_pos} and {len(self.curr_line())} ")
                if self.x_pos >= len(self.curr_line()):
                    return

                self.scroll_if_reach_border()
                self.box.x += 1
                self.stdscr.move(self.box.y,self.box.x)
                return

            if self.box.x > 0:
                self.box.x -= 1
                self.stdscr.move(self.box.y,self.box.x)
                


        # if dir_y != None:
        #     downward(dir_y)
        #     return
        if dir_x != None:
            sideways(dir_x)

    def backspace(self):
        pass

    def write(self):
        pass






class KeyHandler():
    def __init__(self,stdscr:curses.window,box:"Box") -> None:
        self.o = Operations(stdscr,box)
        self.stdscr:curses.window = stdscr
        self.box = box

        c = curses
        self.special_keys = [c.KEY_RIGHT,c.KEY_LEFT]

    def keyHandle(self,key):
            if key ==  -1:
                return "exit"


            if key == curses.KEY_RIGHT:
                self.o.move(dir_x=1)
                pass
                # self.o.move(dir_x=1)
            if key == curses.KEY_LEFT:
                self.o.move(dir_x=-1)
            
            if key not in self.special_keys:
                self.o.put(key)

            self.o.refresh()

            # if key == curses.KEY_UP:
            #     self.o.move(dir_y=-1)
            #     return
            # if key == curses.KEY_DOWN:
            #     self.o.move(dir_y=1)
            #     return

            # if key == curses.KEY_BACKSPACE:
            #     self.o.backspace()
            #     return
            # if key == ord( '\t' ):
            #     self.o.move(dir_y=1)
            #     return

            # if (key == keyc("q")):
            #     return "exit"
                
            # self.o.write(chr(key))


class Box():
    def __init__(self,pad_size:tuple,windowtop:tuple,windowbottom:tuple) -> None:
        self.pad_size = pad_size #y #x

        self.pt = (0,0)

        self.end_pad_row = pad_size[0]
        self.end_pad_col = pad_size[1]

        self.end_win_row = windowbottom[0]
        self.end_win_col = windowbottom[1]

        self.window_top_y = windowtop[0]
        self.window_top_x = windowtop[1]

        self.window_top_y = windowbottom[0]
        self.window_top_x = windowbottom[1]

        self.wt = windowtop
        self.wb = windowbottom
        self.pad = curses.newpad(*pad_size)
        self.x = 0
        self.y = 0 
        self.row_size = pad_size[1] #x
        self.column_size = pad_size[0] #y


        self.keyhandler = KeyHandler(self.pad,self)




def main(stdscr:curses.window):
    # Clear screen
    stdscr.clear()


    # Refresh the standard screen and the new window to make changes visible
    stdscr.refresh()

    # box1 = Box((50,50),(0,0),(curses.LINES-1,curses.COLS-1))
    box1 = Box((50,20),(0,0),(curses.LINES-1,10))
    while (True):
        c = stdscr.getch()
        box1.keyhandler.keyHandle(c)

curses.wrapper(main)
