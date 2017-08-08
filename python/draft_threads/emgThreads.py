from threading import Thread
from multiprocessing import Queue
import time
# from serialCom import serPort
from serial_com import SerialCom
from emgPlot import SetPlot


class ThreadsApp():
  def __init__(self, nChannes=1):

    q = []
    for i in range (0, nChannes):
      q.append(Queue(maxsize=0))

    thread1 = Thread( target=SerialCom, args=("Serial Com", q, nChannes) )
    thread2 = Thread( target=SetPlot, args=("Plots", q, nChannes) )

    thread1.daemon = True
    thread2.daemon = True

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

def main():
  plot = ThreadsApp(8)
  return 0

if __name__ == '__main__':
    main()