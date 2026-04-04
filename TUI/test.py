import ui
from ui import ButtonFocusable, ButtonGlobalKey, Input, Label,Layout, Push,Screen,ScreenHandler,Where
import curses
import logging



with open("program.log","w") as f:
    f.write("")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,filename="program.log")
ui.logger = logger




class Program:

    def __init__(self) -> None:
        pass

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLACK)
        pass



    def initial_layout(self):

        screen = Screen("initial_layout")
        layout = Layout(hasBorder=True,axis='vertical',where=Where.CENTER_OF_SCREEN)

        label = Label("hi")
        signup = ButtonFocusable(text='Sign up',background=1,push=Push(0,0,5,0),hasBorder=True)
        login = ButtonFocusable(text='Log in',background=1)


        
        screen.add_layout(layout)
        layout.add_item(label)
        # layout.add_item(signup)
        # layout.add_item(login)
        self.screenHandler.add_screen(screen)

        



    def main(self,stdsrc:curses.window):

        self.init_colors()
        self.screenHandler = ScreenHandler(stdsrc)
        stdsrc.timeout(100)

        stdsrc.refresh()
        
        # win = curses.newwin(5,5,2,3)
        # win.addstr("hi")
        # win.refresh()



        self.initial_layout()
        self.screenHandler.set_spotlight(screen_name_identifier="initial_layout")

        while(1):
            c = stdsrc.getch()
            if c == -1:
                continue

            self.screenHandler.handleKey(c)




program = Program()
curses.wrapper(program.main)









