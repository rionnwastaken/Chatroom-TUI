from enum import Enum, IntEnum
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



class MC(IntEnum):
    BTNNORMAL = 0
    BTNPRESSED = 1

    



class Program:

    def __init__(self) -> None:
        pass


    def changefg(self):
        # colors = [curses.COLOR_WHITE,curses.COLOR_BLUE,curses.COLOR_CYAN]
        colors = [1,2,3]
        c = 0
        off = True
        def loop():
            nonlocal c,off
            while (True):
                logger.info("running")
                time.sleep(1)
                color = colors[c]

                self.win.bkgd(" ",curses.color_pair(color))
                # curses.init_pair(1,color,curses.COLOR_WHITE)

                
                # if off:
                #     self.win.chgat(0,0,curses.A_UNDERLINE | curses.color_pair(1))
                # else:
                #     self.win.chgat(0,0,curses.A_DIM | curses.color_pair(1))

                # off = not off

                self.win.refresh()


                c += 1
                if c >= len(colors):
                    c = 0
        _thread.start_new_thread(loop,())



    def init_colors(self):

        if curses.has_colors():
            curses.start_color()

        curses.has_extended_color_support()
        curses.use_default_colors()




        # curses.init_color(1,238, 220, 247)
        # curses.use_default_colors()

        curses.init_pair(MC.BTNNORMAL,curses.COLOR_WHITE,-1)
        curses.init_pair(MC.BTNPRESSED,curses.COLOR_WHITE,curses.COLOR_RED)


        # curses.init_pair(1,curses.COLOR_BLUE,-1)
        # curses.init_pair(2, 0, 250)
        # # curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        # curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
        # curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        # curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        # curses.init_pair(6, 200, 100)
    
        
        

        logger.info(f"has colors {curses.has_colors()}, can change color {curses.can_change_color()}, max color {curses.COLORS} extender colors {curses.has_extended_color_support()} longname {curses.longname()}")
        logger.info(f"Color content {curses.color_content(1)}")

        logger.info(f"shit { curses.termattrs()}")


        logger.info(f"COlors are : ?{ curses.COLOR_WHITE,curses.COLOR_BLUE }")





    def create_screens(self,stdsrc):
        self.screenHandler = ScreenHandler(stdsrc)
        self.reusableActions = ReusableActions(self.screenHandler)

        self.initial_layout(stdsrc)



        

    def initial_layout(self,stdsrc):

        self.screenHandler.set_spotlight(screen_name_identifier="initial_layout")


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

        

    def tests(self,stdsrc):

        # self.changefg()
        win = curses.newwin(10,10,2,3)
        win2 = curses.newwin(10,10,6,20)
        self.win = win
        # win.addstr("hi")
        win.bkgd(" ",curses.color_pair(MC.BTNNORMAL))
        win.box()
        win.addstr("buenas",curses.A_DIM)
        win.refresh()

        # win2.bkgd(" ",curses.color_pair(2))

        win2.attrset(curses.color_pair(2))

        win2.addstr("helllo")
        win2.chgat(0,0,curses.A_UNDERLINE | curses.color_pair(MC.BTNNORMAL))

        # curses.curs_set(0)



        # win2.chgat(0,0,2,curses.A_UNDERLINE | curses.color_pair(2))
        # win2.chgat(0,2,1,curses.A_UNDERLINE | curses.color_pair(3))
        # win2.chgat(0,3,1,curses.A_UNDERLINE | curses.color_pair(4))





        win2.refresh()


        curses.setsyx(0, 0)




    def main(
        self,
        stdsrc:curses.window,
    ):

        self.init_colors()
        stdsrc.timeout(100)
        stdsrc.refresh()


        self.tests(stdsrc)
        




        a = 0
        buttonpressed = False
        button_elapsed = 0
        animation_miliseconds = 1000
        while(1):
            start = time.perf_counter()
            c = stdsrc.getch()
            end = time.perf_counter()

            if buttonpressed:
                elapsed = ( end-start ) * 1000
                button_elapsed += elapsed

                logger.info(f"btnelapsed animationml {button_elapsed} {animation_miliseconds}")
                if button_elapsed >= animation_miliseconds:
                    buttonpressed = False
                    button_elapsed = 0
                    self.win.bkgd(" ",curses.color_pair(MC.BTNNORMAL))
                    self.win.refresh()


            # logger.info(f"Time took {end-start}")


            if c == -1:
                continue

            if c == ord( '\n' ):
                logger.info("Pressed?")
                buttonpressed = True
                button_elapsed = 0
                self.win.bkgd(" ",curses.color_pair(MC.BTNPRESSED))
                self.win.refresh()

                

            # self.screenHandler.handleKey(c)




program = Program()
curses.wrapper(program.main)









