from enum import Enum, IntEnum
import curses
import logging
import _thread
import time
import ui
from ui import ButtonFocusable, ButtonGlobalKey, FocusableLayout, GlobalKeyLayout, Input, Label,Layout, Push,Screen,ScreenHandler,Where,ReusableActions


with open("program.log","w") as f:
    f.write("")

# exit(0)




logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,filename="program.log")

logger.info("Logger active?")




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

                # self.win.bkgd(" ",curses.color_pair(color))
                # self.win.erase()

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

        curses.use_default_colors()

        logger.info(f"Color black {curses.COLOR_BLACK}")
        logger.info(f"Color white {curses.COLOR_WHITE}")




        # curses.init_color(1,238, 220, 247)
        # curses.use_default_colors()

        ui.DefaultColors.init()


        # curses.init_pair(MC.BTNNORMAL,curses.COLOR_WHITE,-1)
        # curses.init_pair(MC.BTNPRESSED,curses.COLOR_YELLOW,-1)
        # curses.init_pair(2,curses.COLOR_GREEN,-1)
        # curses.init_pair(3,curses.COLOR_BLUE,-1)

    
        
        

        logger.info(f"has colors {curses.has_colors()}, can change color {curses.can_change_color()}, max color {curses.COLORS} extender colors {curses.has_extended_color_support()} longname {curses.longname()}")
        logger.info(f"Color content {curses.color_content(1)}")

        logger.info(f"shit { curses.termattrs()}")


        logger.info(f"COlors are : ?{ curses.COLOR_WHITE,curses.COLOR_BLUE }")





    def create_screens(self,stdsrc):
        self.screenHandler = ScreenHandler(stdsrc)
        self.ra = ReusableActions(self.screenHandler)

        self.initial_layout(stdsrc)


    def createLayout(self,screen,topy,topx):

        layout = FocusableLayout(hasBorder=True,axis='vertical',coordinates={"topy":topy,"topx":topx})
        signup = ButtonFocusable(text='Sign up',push=Push(0,0,2,0),hasBorder=True)
        login = ButtonFocusable(text='Log in',hasBorder=True)


        screen.add_layout(layout)
        layout.add_item(signup)
        layout.add_item(login)

        login.addAction(callable=self.ra.changeColor3(login,[1,0,3]),key="\n")

    
        def clearScreen():
            screen.get_window().erase()
            screen.get_window().refresh()
            

        login.addAction(callable=clearScreen,key="\n")



        

    def initial_layout(self,stdsrc):



        screen = Screen("initial_layout")
        layout = FocusableLayout(hasBorder=True,axis='vertical',where=Where.CENTER_OF_SCREEN)

        signup = ButtonFocusable(text='Sign up',push=Push(0,0,2,0),hasBorder=True)
        login = ButtonFocusable(text='Log in',hasBorder=True)


        def escpressed():
            logger.info("esc was pressed")

        layout.register_global_key(27,escpressed)

        layout2 = GlobalKeyLayout(hasBorder=True,coordinates={'topx':0,'topy':0})
        btn = ButtonGlobalKey(text="hola",hasBorder=True,global_key_char='a')

        def hi():
            logger.info("hi")

        btn.addAction(hi)


        layout2.add_item(btn)
        screen.add_layout(layout2)



        self.createLayout(screen,10,20)
        self.createLayout(screen,10,30)


        
        # screen.set_spotlight(layout)

        screen.add_layout(layout)
        layout.add_item(signup)
        layout.add_item(login)

        login.addAction(callable=self.ra.changeColor3(login,[1,0,3]),key="\n")

    
        def clearScreen():
            screen.get_window().erase()
            screen.get_window().refresh()
            

        login.addAction(callable=clearScreen,key="\n")

        self.screenHandler.add_screen(screen)


        self.screenHandler.set_spotlight(screen_name_identifier="initial_layout")


        while(1):
            start = time.perf_counter()
            c = stdsrc.getch()
            end = time.perf_counter()


            if c == -1:
                continue

            self.screenHandler.handleKey(c)


        

    def tests(self,stdsrc):

        # self.changefg()
        win = curses.newwin(10,10,2,3)
        win2 = curses.newwin(10,10,6,20)
        self.win = win
        # win.addstr("hi")
        win.bkgd(" ",curses.color_pair(MC.BTNNORMAL))
        win.border('#','#','#','#','#','#','#','#',)

        curses.init_pair(200,curses.COLOR_RED,-1)
        curses.init_pair(201,curses.COLOR_WHITE,-1)
        curses.init_pair(202,curses.COLOR_WHITE,-1)
        win.addstr(1,1,"buenas",  curses.color_pair(1))
        # win.chgat(1,1,200)

        win.refresh()







        # win2.refresh()


        # curses.setsyx(0, 0)


        a = 0
        buttonpressed = False
        button_elapsed = 0
        animation_miliseconds = 200
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
                # self.win.erase()
                self.win.refresh()

                

            # self.screenHandler.handleKey(c)


    

    def e(self,stdsrc:curses.window):

        def _getcolor():
            colors = [2,3,1]
            pos = 0

            def i():
                nonlocal pos
                color = colors[pos]
                pos += 1
                if pos >= len(colors):
                    pos = 0

                return color
            return i

        getcolor = _getcolor()

        win = curses.newwin(10,10,3,5)
        win.box()


        win2 = win.derwin(4,4,0,0)
        win2.addstr("he")
        win2.box()

        curses.init_pair(4,curses.COLOR_GREEN,-1)
        curses.init_pair(5,curses.COLOR_WHITE,-1)

        win2.bkgd(" ",curses.color_pair(1))
        # win.bkgd(" ",curses.color_pair(0))
        win.refresh()
        win2.refresh()

        while(1):
            start = time.perf_counter()
            c = stdsrc.getch()
            end = time.perf_counter()


            if c == -1:
                continue

            if c == ord('\n'):
                win.bkgd(" ",curses.color_pair(getcolor()))
                win.refresh()





    def main(
        self,
        stdsrc:curses.window,
    ):

        self.init_colors()
        stdsrc.timeout(100)
        stdsrc.refresh()

        # self.e(stdsrc)

        # self.tests(stdsrc)
        self.create_screens(stdsrc)
        







program = Program()
curses.wrapper(program.main)









