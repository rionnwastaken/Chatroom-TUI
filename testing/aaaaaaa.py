import curses

def main(win):
    # 1. Initialize color support
    if curses.has_colors():
        curses.start_color()

    # 2. Define a color pair (Pair 1: White foreground, Blue background)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)

    # 3. Apply the color pair to the window's background
    # The first argument is the character to use for blank spaces (here, a space ' ')
    # The second argument combines the color pair attribute
    win.bkgd(' ', curses.color_pair(1))

    # Add some text to verify the background
    win.addstr(1, 1, "The background is now blue with white text.")
    win.getch() # Wait for user input

if __name__ == '__main__':
    curses.wrapper(main)
