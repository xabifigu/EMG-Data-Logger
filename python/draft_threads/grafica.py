# """
# =====
# Decay
# =====

# This example showcases a sinusoidal decay animation.
# """


# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

# from threading import Thread
# from multiprocessing import Queue

# class setPlot():

#   # chToShow = 0

#   def __init__(self, name, q, num):
#     self.q = q
#     self.chToShow = num
#     self.nbPlots = num
#     self.startAnimation()

#   def data_gen(self, t=0):
#     cnt = 0
#     x = 0
#     # while cnt < 1000:
#     #     cnt += 1
#     #     t += 0.1
#     #     yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)
#     stopLoop = False
#     while True:
#     # while not self.q.empty():
#       # x = input('number: ')
      
#       # el dato recibido es un array de dos simiensiones:
#       # x[0]: tiempo en milisegundos
#       # x[1]: dato ADC
#       x = self.q.get()
      
#       if x == None:
#         self.ani.event_source.stop() 
#         raise StopIteration

#       cnt += 1
      
#       print("Grafica: " + str(cnt) + " valor: " + str(x))
#       # yield cnt, x
#       yield x[0], x[1]

#   def init(self):
#       self.ax[self.chToShow].set_ylim(0, 4250)
#       self.ax[self.chToShow].set_xlim(0, 2000)

#       # self.ax[1].set_ylim(0, 4250)
#       # self.ax[1].set_xlim(0, 2000)

#       del self.xdata[:]
#       del self.ydata[:]
#       self.line.set_data(self.xdata, self.ydata)
#       return self.line,

#   def run(self, data):
#       # update the data
#       t, y = data
#       self.xdata.append(t)
#       self.ydata.append(y)
#       xmin, xmax = self.ax[self.chToShow].get_xlim()

#       if t >= xmax:
#           # self.ax.set_xlim(xmin, 2*xmax)
#           self.ax[self.chToShow].set_xlim(xmin, xmax+2000)
#           # self.ax.set_xlim(xmax, xmax+250)
#           self.ax[self.chToShow].figure.canvas.draw()
#       self.line.set_data(self.xdata, self.ydata)

#       return self.line,

#   def startAnimation(self):
#     # thisFig = plt.figure(self.chToShow)

#     # if self.chToShow != 0:
#     #   plt.figure(self.chToShow)

#     # self.fig, self.ax = plt.subplots()
#     # self.line, = self.ax.plot([], [], lw=2)
#     # self.ax.grid()
#     # self.xdata, self.ydata = [], []

#     self.fig, self.ax = plt.subplots(nrows=2, ncols=1, sharex='all', sharey='all')
#     self.line, = self.ax[self.chToShow].plot([], [], lw=2)
#     self.ax[self.chToShow].grid()

#     # self.line, = self.ax[1].plot([], [], lw=2)
#     # self.ax[1].grid()

#     self.xdata, self.ydata = [], []

#     title = 'Channel' + str(self.chToShow)
#     self.fig.suptitle(title, fontsize=18)
#     plt.xlabel('time (ms)')
#     plt.ylabel('value')

#     self.ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=False, interval=10,
#                                   repeat=False, init_func=self.init)
#     # if self.chToShow == 1:
#     #   plt.show()
#     plt.show()

# def main():
#   name = "Plot-1"
#   queue = Queue()
#   queue.put(None)
#   plot = setPlot(name, queue, 0)
#   return 0

# if __name__ == '__main__':
#     main()



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

  # chToShow = 0

  def __init__(self, name, q, num):
    self.q = q
    self.chToShow = num
    self.nbCh = num
    self.startAnimation()

  def data_gen(self, t=0):
    cnt = 0
    x = []

    for i in range (0, self.nbCh):
      x.append(None)
      x[i] = [0,0]

    while True:
    # while not self.q.empty():
      # x = input('number: ')
      
      # el dato recibido es un array de dos simiensiones:
      # x[i][0]: tiempo en milisegundos
      # x[i][1]: dato ADC
      for i in range(0, self.nbCh):
        if not self.q[i].empty():
          x[i] = self.q[i].get()
        
        print("Canal: " + str(i) + " valor: " + str(x[i]))
      
        if x[i] == None:
          self.ani.event_source.stop() 
          raise StopIteration

      cnt += 1
      
      print("Grafica: " + str(cnt) + " valor: " + str(x))
      # yield cnt, x
      # yield x[0], x[1]
      yield x

  def init(self):
    for i in range(0, self.nbCh):
      self.arAx[i].set_ylim(0, 4250)
      self.arAx[i].set_xlim(0, 2000)

      # self.ax[1].set_ylim(0, 4250)
      # self.ax[1].set_xlim(0, 2000)

      del self.arDataX[i][:]
      del self.arDataY[i][:]
      self.arLine[i].set_data(self.arDataX[i], self.arDataY[i])

    # return self.line,
    return self.arLine

  def run(self, data):
      # update the data
      # t, y = data

      # self.arDataX[0].append(t)
      # self.arDataY[0].append(y)
      # xmin, xmax = self.arAx[0].get_xlim()

      # if t >= xmax:
      #     # self.ax.set_xlim(xmin, 2*xmax)
      #     self.arAx[0].set_xlim(xmin, xmax+2000)
      #     # self.ax.set_xlim(xmax, xmax+250)
      #     self.arAx[0].figure.canvas.draw()
      # self.arLine[0].set_data(self.arDataX[0], self.arDataY[0])

      for i in range(0, self.nbCh):
        t, y = data[i]
        self.arDataX[i].append(t)
        self.arDataY[i].append(y)
        xmin, xmax = self.arAx[i].get_xlim()

        if t >= xmax:
            # self.ax.set_xlim(xmin, 2*xmax)
            self.arAx[i].set_xlim(xmin, xmax+2000)
            # self.ax.set_xlim(xmax, xmax+250)
            self.arAx[i].figure.canvas.draw()
        self.arLine[i].set_data(self.arDataX[i], self.arDataY[i])

      # return self.line,
      return self.arLine

  def startAnimation(self):
    self.arAx = []
    self.arLine = []
    self.arDataX = []
    self.arDataY = []

    fig = plt.figure()
    title = 'EMG Data'
    fig.suptitle(title, fontsize=18)

    for i in range(0, self.nbCh):
      self.arAx.append(None)
      self.arLine.append(None)
      self.arDataX.append(None)
      self.arDataY.append(None)

      self.arAx[i] = fig.add_subplot(self.nbCh, 1, i+1)
      self.arAx[i].set_xlabel('time (ms)')
      self.arAx[i].set_ylabel('channel ' + str(i))
      self.arAx[i].grid()

      self.arLine[i], = self.arAx[i].plot([], [], lw=2)

      self.arDataX[i], self.arDataY[i] = [], []



    # self.fig, self.ax = plt.subplots(nrows=2, ncols=1, sharex='all', sharey='all')
    # self.line, = self.ax[self.chToShow].plot([], [], lw=2)
    # self.ax[self.chToShow].grid()

    # self.xdata, self.ydata = [], []

    self.ani = animation.FuncAnimation(fig, self.run, self.data_gen, blit=False, interval=10,
                                  repeat=False, init_func=self.init)
    # if self.chToShow == 1:
    #   plt.show()
    plt.show()

def main():
  name = "Plot-1"
  queue = Queue()
  queue.put(None)
  plot = setPlot(name, queue, 2)
  return 0

if __name__ == '__main__':
    main()