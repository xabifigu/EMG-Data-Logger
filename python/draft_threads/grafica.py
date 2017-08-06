"""
=====
Decay
=====

This example showcases a sinusoidal decay animation.
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from threading import Thread
from multiprocessing import Queue

class setPlot():

  chToShow = 0

  def __init__(self, name, q, chToShow=0):
    self.q = q
    self.startAnimation()
    self.chToShow = chToShow

  def data_gen(self, t=0):
    cnt = 0
    x = 0
    # while cnt < 1000:
    #     cnt += 1
    #     t += 0.1
    #     yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)
    stopLoop = False
    while True:
    # while not self.q.empty():
      # x = input('number: ')
      
      # el dato recibido es un array de dos simiensiones:
      # x[0]: tiempo en milisegundos
      # x[1]: dato ADC
      x = self.q.get()
      
      if x == None:
        self.ani.event_source.stop() 
        raise StopIteration

      cnt += 1
      
      print("Grafica: " + str(cnt) + " valor: " + str(x))
      # yield cnt, x
      yield x[0], x[1]

  def init(self):
      self.ax.set_ylim(0, 4250)
      self.ax.set_xlim(0, 2000)
      del self.xdata[:]
      del self.ydata[:]
      self.line.set_data(self.xdata, self.ydata)
      return self.line,

  def run(self, data):
      # update the data
      t, y = data
      self.xdata.append(t)
      self.ydata.append(y)
      xmin, xmax = self.ax.get_xlim()

      if t >= xmax:
          # self.ax.set_xlim(xmin, 2*xmax)
          self.ax.set_xlim(xmin, xmax+2000)
          # self.ax.set_xlim(xmax, xmax+250)
          self.ax.figure.canvas.draw()
      self.line.set_data(self.xdata, self.ydata)

      return self.line,

  def startAnimation(self):
    self.fig, self.ax = plt.subplots()
    self.line, = self.ax.plot([], [], lw=2)
    self.ax.grid()
    self.xdata, self.ydata = [], []

    title = 'Channel' + str(self.chToShow)
    self.fig.suptitle(title, fontsize=18)
    plt.xlabel('time (ms)')
    plt.ylabel('value')

    self.ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=False, interval=10,
                                  repeat=False, init_func=self.init)
    plt.show()

def main():
  name = "Thread-1"
  queue = Queue()
  queue.put(None)
  plot = setPlot(name, queue)
  return 0

if __name__ == '__main__':
    main()