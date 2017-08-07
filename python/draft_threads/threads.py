from threading import Thread
from multiprocessing import Queue
import time
# from serialCom import serPort
from serial_com import SerialCom
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


# def plotCh0 (threadname, q, ch):
#   setPlot(threadname, q, ch)

# def plotCh1 (threadname, q, ch):
#   setPlot(threadname, q, ch)


q = [None]
for i in range (0, 2):
  q.append(Queue(maxsize=0))
del q[0]

# queue = Queue(maxsize=0)


thread1 = Thread( target=SerialCom, args=("Serial Com", q) )

thread2 = Thread( target=setPlot, args=("Thread-2", q, 2) )

# thread2 = Thread( target=setPlot, args=("Thread-2", queue[0], 0) )
# thread3 = Thread( target=setPlot, args=("Thread-3", queue[1], 1) )

# thread2 = Thread( target=plotCh0, args=("Plot 0", queue[0], 0) )
# thread3 = Thread( target=plotCh1, args=("Plot 1", queue[1], 1) )

print('as')

thread1.daemon = True
thread2.daemon = True
# thread3.daemon = True

thread1.start()
thread2.start()
# thread3.start()

thread1.join()
thread2.join()
# thread3.join()