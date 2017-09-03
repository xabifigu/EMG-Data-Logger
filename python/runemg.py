# !/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cbook as cbook

import glob
import os
import sys

from threading import Thread
from multiprocessing import Queue

from serial_com import SerialCom

# conversor de csv a gráfica
def csv2Plot(path='.\\', extension='emgdat'):
  """ 
  @def    Busca todos los archivos con extensión 'extension'
          dentro de la ruta 'path'. Mustra una gráfica por cada
          archivo encontrado.
  @arg    path  ruta donde buscar los ficheros
          extension extensión de los ficheros a buscar
  @return True si encuentra fichero con extensión
          False si no ecneuntra fichero con extensión
  """
  ret = False
  filesDir = path + '\\*.' + extension
  if not glob.glob(filesDir):
    # no se encuentran ficheros
    pass
  else:
    # una gráfica por cada fichero
    for f in glob.glob(filesDir):
      i = 0
      fName = cbook.get_sample_data(f, asfileobj=False)
      plt.plotfile(fName, cols=(0,1), delimiter=',', names=['t(ms)', 'value'], newfig=True)
      plt.title(fName, fontsize=8)
      plt.grid()
      i += 1
    plt.show()
    ret = True
  return ret

class SetPlot():
  """
  Clase para mostrar gráfricas en tiempo real
  """
  def __init__(self, q, nCh2Show=1, vMax=0, rGain=0):
    """ 
    Método inicial de la clase
    """
    self.q = q
    self.nCh2Show = nCh2Show

    # si vMax es 0, se muestran los datos en función del
    # valor devuelto por el ADC
    if vMax == 0:
      self.vMax = 4095
    else:
      self.vMax = vMax

    # si rGain es 0, no se calcula el valor en función 
    # de la ganancia
    if rGain == 0:
      self.gain = 1
    else:
      self.gain = 201 * rGain / 1000

    self.startAnimation() # inicia la representación

  def data_gen(self):
    """ 
    @def    Generar datos para alimentnar la gráfica.
            Estos datos proceden de colas.
    @arg    none
    @return datos nuevos
    """
    x = []

    for i in range (0, self.nCh2Show):
      x.append(None)
      x[i] = [0,0]

    while True:
      # el dato recibido es un array de dos simiensiones:
      # x[i][0]: tiempo en milisegundos
      # x[i][1]: dato ADC
      for i in range(0, self.nCh2Show):
        if not self.q[i].empty():
          x[i] = self.q[i].get()
      
        if x[i] == None:
          # no se reciben datos nuevos, se para la gráfica
          self.ani.event_source.stop() 
          raise StopIteration
      yield x

  def init(self):
    """ 
    @def    Inicializa los datos de la gráfica
    @arg    none
    @return lineas a dibujar
    """
    # inicialización de datos para la gráfica
    yMax = self.vMax / self.gain
    yMax = yMax + (yMax * 0.05)
    for i in range(0, self.nCh2Show):
      self.arAx[i].set_ylim(0, yMax)
      self.arAx[i].set_xlim(0, 5000)

      del self.arDataX[i][:]
      del self.arDataY[i][:]
      self.arLine[i].set_data(self.arDataX[i], self.arDataY[i])

    return self.arLine

  def run(self, data):
    """ 
    @def    Actualización de datos de la gráfica
    @arg    data nuevos datos a integrar
    @return lineas a dibujar
    """
    # actualizar datos
    # se actualizan los datos de cada canal
    for i in range(0, self.nCh2Show):
      t, y = data[i]
      self.arDataX[i].append(t)
      self.arDataY[i].append(y)
      xmin, xmax = self.arAx[i].get_xlim()

      # si se ha llegado al límite del eje x, se agranda la gráfica en el eje x
      if t >= xmax:
          self.arAx[0].set_xlim(xmin, xmax+2000)
          self.arAx[0].figure.canvas.draw()
      self.arLine[i].set_data(self.arDataX[i], self.arDataY[i])

    return self.arLine

  def startAnimation(self):
    """ 
    @def    Inicializa la animación (gráfica en tiempo real)
    @arg    none
    @return none
    """
    # se crean los arrays
    self.arAx     = []
    self.arLine   = []
    self.arDataX  = []
    self.arDataY  = []

    # se crea la figura en la que se mostrará la gráfica
    fig = plt.figure()
    title = 'EMG Data'
    fig.suptitle(title, fontsize=10)

    # se crean tantas gráficas como canales se quieran visualizar
    for i in range(0, self.nCh2Show):
      self.arAx.append(None)
      self.arLine.append(None)
      self.arDataX.append(None)
      self.arDataY.append(None)

      # todos los subplots comparten el eje x
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


class ThreadsApp():
  """
  Clase para crear el hilo secundario y esperar a que finalice
  """
  def __init__(self, nChannels=8, nCh2Show=1,
            comPort='COM8', bauds=9600,
            outFolder='.\\', vMax=0, rGain=0):
    """ 
    Método inicial de la clase.
    Crea las colas necesarias, y crea y ejecuta el hilo secudnario.
    """
    # Se crean las colas que enviarán los datos recogidos
    # por el módulo puerto serie a la gráfica en tiempo real.
    # Se crean tantas colas como canales se quieren visualizar
    q = []
    for i in range (0, nCh2Show):
      q.append(Queue(maxsize=0))

    # Se crea el hilo secundario, el cual recolecta los datos
    # recibidos por el puerto serie.
    thread1 = Thread( target=SerialCom, args=("Serial Com", q, 
                                              nChannels, nCh2Show,
                                              comPort, bauds,
                                              outFolder,
                                              vMax, rGain) )
    thread1.daemon = True
    thread1.start() # se inicia el hilo

    SetPlot(q, nCh2Show, vMax, rGain)  # iniciar gráfica en tiempo real

    thread1.join()  # esperar a que termine el hilo secundario

if __name__ == '__main__':
    """
    Se evaluan los argumentos con los que se ejecuta este script
    """
    # print(sys.argv) # @note traza
    if len(sys.argv) == 1:
      ThreadsApp()
    elif len(sys.argv) == 2:
      ThreadsApp(int(sys.argv[1]))
    elif len(sys.argv) == 3:
      ThreadsApp(int(sys.argv[1]), int(sys.argv[2]))
    elif len(sys.argv) == 4:
      ThreadsApp(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    elif len(sys.argv) == 5:
      ThreadsApp(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                int(sys.argv[4]))
    elif len(sys.argv) == 6:
      ThreadsApp(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) == 7:
      ThreadsApp(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                int(sys.argv[4]), sys.argv[5], float(sys.argv[6]))
    elif len(sys.argv) == 8:
      ThreadsApp(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                int(sys.argv[4]), sys.argv[5], float(sys.argv[6]), float(sys.argv[7]))
    else:
      print("Incorrect number of arguments")