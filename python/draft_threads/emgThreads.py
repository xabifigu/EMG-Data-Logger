from threading import Thread
from multiprocessing import Queue
import time
# from serialCom import serPort
from serial_com import SerialCom
from emgPlot import SetPlot


class ThreadsApp():
  def __init__(self, nChannes=1):

    q = [None]
    for i in range (0, 2):
      q.append(Queue(maxsize=0))
    del q[0]

    thread1 = Thread( target=SerialCom, args=("Serial Com", q, 1) )

    thread2 = Thread( target=SetPlot, args=("Plots", q, 1) )

    # thread2 = Thread( target=setPlot, args=("Thread-2", queue[0], 0) )
    # thread3 = Thread( target=setPlot, args=("Thread-3", queue[1], 1) )

    # thread2 = Thread( target=plotCh0, args=("Plot 0", queue[0], 0) )
    # thread3 = Thread( target=plotCh1, args=("Plot 1", queue[1], 1) )

    thread1.daemon = True
    thread2.daemon = True
    # thread3.daemon = True

    thread1.start()
    thread2.start()
    # thread3.start()

    thread1.join()
    thread2.join()
    # thread3.join()

def main():
  plot = ThreadsApp(1)
  return 0

if __name__ == '__main__':
    main()