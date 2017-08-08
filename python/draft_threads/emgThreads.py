from threading import Thread
from multiprocessing import Queue
import time
# from serialCom import serPort
from serial_com import SerialCom
from emgPlot import SetPlot


class ThreadsApp():
  def __init__(self, nChannels=8, nCh2Show=1,
              comPort='COM8', bauds=9600,
              outFolder='.\\'):

    q = []
    for i in range (0, nCh2Show):
      q.append(Queue(maxsize=0))

    thread1 = Thread( target=SerialCom, args=("Serial Com", q, 
                                              nChannels, nCh2Show,
                                              comPort, bauds,
                                              outFolder) )
    thread2 = Thread( target=SetPlot, args=("Plots", q, nCh2Show) )

    thread1.daemon = True
    thread2.daemon = True

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

def main():
  plot = ThreadsApp()
  return 0

if __name__ == '__main__':
    main()