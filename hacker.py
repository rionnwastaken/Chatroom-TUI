import queue
import _thread
import time



q = queue.Queue()

def a ():
    count = 0
    while (True):
        time.sleep(1)
        count += 1
        if count >= 3:
            q.put("hola")
            q.put("chuta")
            print("breaking")
            break

_thread.start_new_thread(a,())


v = q.get()
print(v)
