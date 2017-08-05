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

  def __init__(self, name, q):
    self.q = q
    self.startAnimation()

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
      x = self.q.get()
      
      if x == None:
        self.ani.event_source.stop() 
        raise StopIteration
    
      # if self.q.empty():
      #   self.ani.event_source.stop() 
      #   stopLoop = True
      #   break
      cnt += 1
      # print(x)
      print("Grafica: " + str(cnt) + " valor: " + str(x))
      yield cnt, x

  def init(self):
      self.ax.set_ylim(0, 4250)
      self.ax.set_xlim(0, 250)
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
          self.ax.set_xlim(xmin, 2*xmax)
          self.ax.figure.canvas.draw()
      self.line.set_data(self.xdata, self.ydata)

      return self.line,

  def startAnimation(self):
    self.fig, self.ax = plt.subplots()
    self.line, = self.ax.plot([], [], lw=2)
    self.ax.grid()
    self.xdata, self.ydata = [], []

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