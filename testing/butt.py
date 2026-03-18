

import curses
import locale
import sys

def main(filename, filecontent, encoding="utf-8"):
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(1)
        rows, columns = stdscr.getmaxyx()
        stdscr.border()
        bottom_menu = u"(↓) Next line | (↑) Previous line | (→) Next page | (←) Previous page | (q) Quit".encode(encoding).center(columns - 4)
        stdscr.addstr(rows - 1, 2, bottom_menu, curses.A_REVERSE)
        out = stdscr.subwin(rows - 2, columns - 2, 1, 1)
        out_rows, out_columns = out.getmaxyx()
        out_rows -= 1
        lines = map(lambda x: x + " " * (out_columns - len(x)), reduce(lambda x, y: x + y, [[x[i:i+out_columns] for i in xrange(0, len(x), out_columns)] for x in filecontent.expandtabs(4).splitlines()]))
        stdscr.refresh()
        line = 0
        while 1:
            top_menu = (u"Lines %d to %d of %d of %s" % (line + 1, min(len(lines), line + out_rows), len(lines), filename)).encode(encoding).center(columns - 4)
            stdscr.addstr(0, 2, top_menu, curses.A_REVERSE)
            out.addstr(0, 0, "".join(lines[line:line+out_rows]))
            stdscr.refresh()
            out.refresh()
            c = stdscr.getch()
            if c == ord("q"):
                break
            elif c == curses.KEY_DOWN:
                if len(lines) - line > out_rows:
                    line += 1
            elif c == curses.KEY_UP:
                if line > 0:
                    line -= 1
            elif c == curses.KEY_RIGHT:
                if len(lines) - line >= 2 * out_rows:
                    line += out_rows
            elif c == curses.KEY_LEFT:
                if line >= out_rows:
                    line -= out_rows
    finally:
        curses.nocbreak(); stdscr.keypad(0); curses.echo(); curses.curs_set(1)
        curses.endwin()

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    encoding = locale.getpreferredencoding()
    try:
        filename = sys.argv[1]
    except:
        print ( "Usage: python %s FILENAME" ) 
    else:
        try:
            with open(filename) as f:
                filecontent = f.read()
        except:
            print ( "Unable to open file %s" )
        else:
            main(filename, filecontent, encoding)
