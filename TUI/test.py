import ui
from ui import ButtonFocusable, ButtonGlobalKey, Input, Label,Layout, Push,Screen,ScreenHandler,Where,ReusableActions
import curses
import logging
import _thread
import time



with open("program.log","w") as f:
    f.write("")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,filename="program.log")
ui.logger = logger




class Program:

    def __init__(self) -> None:
        pass


    def changefg(self):
        colors = [curses.COLOR_WHITE,curses.COLOR_BLUE,curses.COLOR_CYAN]
        c = 0
        def loop():
            nonlocal c
            while (True):
                logger.info("running")
                time.sleep(1)
                color = colors[c]
                curses.init_pair(1,curses.COLOR_WHITE,color)
                self.win.refresh()

                c += 1
                if c >= len(colors):
                    c = 0
        _thread.start_new_thread(loop,())



    def init_colors(self):

        if curses.has_colors():
            curses.start_color()

        curses.has_extended_color_support()


        curses.init_color(1,238, 220, 247)
        # curses.use_default_colors()
        curses.init_pair(1,curses.COLOR_BLUE,1)
        curses.init_pair(2, 0, 250)
        # curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(6, 200, 100)
    
        
        

        logger.info(f"has colors {curses.has_colors()}, can change color {curses.can_change_color()}, max color {curses.COLORS} extender colors {curses.has_extended_color_support()} longname {curses.longname()}")
        logger.info(f"Color content {curses.color_content(1)}")


        logger.info(f"COlors are : ?{ curses.COLOR_WHITE,curses.COLOR_BLUE }")







        

    def initial_layout(self):

        screen = Screen("initial_layout")
        layout = Layout(focusable=True,hasBorder=True,axis='vertical',where=Where.CENTER_OF_SCREEN)

        label = Label("hi")
        signup = ButtonFocusable(text='Sign up',background=2,push=Push(0,0,2,0),hasBorder=True)
        login = ButtonFocusable(text='Log in',background=2,hasBorder=True)





        
        # screen.set_spotlight(layout)

        screen.add_layout(layout)
        layout.add_item(signup)
        layout.add_item(login)

        self.screenHandler.add_screen(screen)

        



    def main(self,stdsrc:curses.window):

        self.init_colors()
        stdsrc.timeout(100)
        stdsrc.refresh()
        
        self.changefg()
        win = curses.newwin(5,5,2,3)
        win2 = curses.newwin(5,5,6,20)
        self.win = win
        # win.addstr("hi")
        win.bkgd(" ",curses.color_pair(1))
        win.addch(curses.ACS_BULLET,curses.A_ITALIC)
        win.refresh()

        win2.bkgd(" ",curses.color_pair(1))
        win2.addch("h")
        win2.refresh()

        # curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)


        # self.screenHandler = ScreenHandler(stdsrc)
        # self.reusableActions = ReusableActions(self.screenHandler)
        # self.initial_layout()
        # self.screenHandler.set_spotlight(screen_name_identifier="initial_layout")


        while(1):
            c = stdsrc.getch()
            if c == -1:
                continue

            # self.screenHandler.handleKey(c)




program = Program()
curses.wrapper(program.main)









