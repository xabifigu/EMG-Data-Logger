import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from threading import Thread
from multiprocessing import Queue

class SetPlot():
  def __init__(self, name, q, nCh2Show=1):
    self.q = q
    # self.chToShow = nCh2Show
    self.nCh2Show = nCh2Show
    self.startAnimation()

  def data_gen(self, t=0):
    cnt = 0
    x = []

    for i in range (0, self.nCh2Show):
      x.append(None)
      x[i] = [0,0]

    while True:
    # while not self.q.empty():
      # x = input('number: ')
      
      # el dato recibido es un array de dos simiensiones:
      # x[i][0]: tiempo en milisegundos
      # x[i][1]: dato ADC
      for i in range(0, self.nCh2Show):
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
    for i in range(0, self.nCh2Show):
      self.arAx[i].set_ylim(0, 4250)
      self.arAx[i].set_xlim(0, 2000)

      del self.arDataX[i][:]
      del self.arDataY[i][:]
      self.arLine[i].set_data(self.arDataX[i], self.arDataY[i])

    # return self.line,
    return self.arLine

  def run(self, data):
      # update the data
      for i in range(0, self.nCh2Show):
        t, y = data[i]
        self.arDataX[i].append(t)
        self.arDataY[i].append(y)
        xmin, xmax = self.arAx[i].get_xlim()

        if t >= xmax:
            # self.arAx[i].set_xlim(xmin, xmax+2000)
            # self.arAx[i].figure.canvas.draw()
            self.arAx[0].set_xlim(xmin, xmax+2000)
            self.arAx[0].figure.canvas.draw()
        self.arLine[i].set_data(self.arDataX[i], self.arDataY[i])

      # return self.line,
      return self.arLine

  def startAnimation(self):
    self.arAx     = []
    self.arLine   = []
    self.arDataX  = []
    self.arDataY  = []

    fig = plt.figure()
    title = 'EMG Data'
    fig.suptitle(title, fontsize=18)

    for i in range(0, self.nCh2Show):
      self.arAx.append(None)
      self.arLine.append(None)
      self.arDataX.append(None)
      self.arDataY.append(None)

      # todos los bubplots comparte el eje x
      if i is 0:
        self.arAx[i] = fig.add_subplot(self.nCh2Show, 1, i+1)
      else:
        self.arAx[i] = fig.add_subplot(self.nCh2Show, 1, i+1, sharex=self.arAx[0])
      self.arAx[i].set_xlabel('t(ms)')
      self.arAx[i].set_ylabel('ch ' + str(i))
      self.arAx[i].grid()

      self.arLine[i], = self.arAx[i].plot([], [], lw=1)

      self.arDataX[i], self.arDataY[i] = [], []

    # iniciar animación
    self.ani = animation.FuncAnimation(fig, self.run, self.data_gen, blit=False, interval=10,
                                  repeat=False, init_func=self.init)
    # mostrar plots
    plt.show()

def main():
  name = "Plot-1"
  q = []
  q.append(Queue())
  q[0].put(None)
  plot = SetPlot(name, q)
  return 0

if __name__ == '__main__':
    main()