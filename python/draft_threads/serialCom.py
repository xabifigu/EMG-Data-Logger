import serial
# import binascii
import time
import numpy as np
import matplotlib.pyplot as plt

from threading import Thread
from multiprocessing import Queue

class serPort():

  MAX_CHANNELS = 8

  def __init__(self, name, q):
    ser = serial.Serial()
    ser.baudrate = 9600
    #ser.port = serialPort
    ser.port = 'COM8'
    ser.timeout = 1

    # tiempo entre cada dato: 
    # tiempo entre cada bit = 1/baudrate
    # número de bit por dato = 10
    # Dato en milisegundos
    newDataPeriod_ms = ((1 / ser.baudrate) * 10) * 1000

    # f = open('test.csv', 'w')

    isSerialOpen = False
    try:
      ser.open()
      isSerialOpen = True
    except:
      print('Error abriendo puerto serie')

    # sincronizar datos del puerto serie
    if isSerialOpen == True:
      numberReadCh = 0
      nextCh = 0
      dataWithCh = True
      # se han de leer los canales de forma consecutiva,
      # teniendo en cuenta, que el número de canal se guarda
      # en nibble más significativo, y el número canal se
      # recibe cada dos bytes
      while numberReadCh < self.MAX_CHANNELS:
        # leer dato y obtener el número de canal
        x = ser.read()
        # numberOfCh = 99
        # si no se leyó ningún dato, se acaba el bucle
        if len(x) < 1:
          isSerialOpen = False
          break
        if dataWithCh is True:
          numberOfCh = self.getHighNibbleFromByte(ord(x))
          if numberOfCh == 0:
            nextCh = numberOfCh
          else:
            pass
          if numberOfCh < self.MAX_CHANNELS and numberOfCh == nextCh:
            dataWithCh = False
            numberReadCh += 1
            if nextCh == (self.MAX_CHANNELS-1):
              nextCh = 0
            else:
              nextCh = numberOfCh+1
            print ('Correcto: ' + str(numberOfCh))
          else:
            # no se ha leído un número válido
            numberReadCh = 0
            # nextCh = 0
            # numberOfCh = 55
            print('Canal no válido: ' + str(numberOfCh))
        else:
          dataWithCh = True
          print('Canal no esperado')
      
        # print (str(numberOfCh))
    else:
      pass

    if isSerialOpen is True:
      # el primer byte no es canal
      x = ser.read()
      cnt = 0
      cntCh0 = 0
      while True:
        arr = ser.read(2)
        if len(arr) < 2:
          print ("No more data")
          break
        else:
          chNum, adcValue = self.getProcessReadData(arr)
          if chNum == 0:
            if q.empty():
              q.put(adcValue)
            cntCh0 += 1
          else:
            pass      
          cnt += 1 
          print("Serial: " + str(cnt) + " Ch0: " + str(cntCh0))
          
      q.put(None) 
    else:
      pass

    # if isSerrialOpen == True:
    #   cnt = 0
    #   while True:
    #     x = ser.read(1)
    #     if len(x) < 1:
    #       print ("No more data")
    #       break
    #     else:
    #       q.put(ord(x))
    #       cnt += 1
    #     y = int.from_bytes(x, byteorder='big', signed=False)
    #     # print('Serial: ' + str(y))
    #     f.write(str(y) + "\n")
    #     print("Serial: " + str(cnt))

      # q.put(None)

      # if not (ser.closed):
      #   ser.close()
      
      # f.close()

    # else:
    #   pass
    
    if not (ser.closed):
      ser.close()
    print ('Fin recepción datos!')

  def getHighNibbleFromByte(self, data):
    """ 
    @def 
    @arg 
    @return 
    """
    x = data & 0xF0
    return (x >> 4)
  #
  def getLowNibbleFromByte(self, data):
    """ 
    @def 
    @arg 
    @return 
    """
    return (data & 0x0F)

  #
  def  bytes2Word(self, highByte, lowByte):
    """ 
    @def 
    @arg 
    @return 
    """
    x = highByte << 8
    return (x | lowByte)

  #
  def getProcessReadData(self, arData):
    """ 
    @def 
    @arg 
    @return 
    """
    ch = self.getHighNibbleFromByte(arData[0])

    aux = self.getLowNibbleFromByte(arData[0])
    value = self.bytes2Word(aux,arData[1])
    return ch, value

def main():
  name = "Thread-1"
  queue = Queue()
  plot = serPort(name, queue)
  return 0

if __name__ == '__main__':
    main()