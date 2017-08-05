from threading import Thread
from multiprocessing import Queue
import time
from serialCom import serPort
from grafica import setPlot

# def thread1(threadname, q):
#     #read variable "a" modify by thread 2
#     while True:
#         a = q.get()
#         if a is None: return # Poison pill
#         print (a)

# def thread2(threadname, q):
#     a = 0
#     for _ in range(10):
#         a += 1
#         q.put(a)
#         time.sleep(0.25)
#     q.put(None) # Poison pill

queue = Queue(maxsize=0)
thread1 = Thread( target=serPort, args=("Thread-1", queue) )
thread2 = Thread( target=setPlot, args=("Thread-2", queue) )

thread1.daemon = True
thread2.daemon = True

thread1.start()
thread2.start()
thread1.join()
thread2.join()