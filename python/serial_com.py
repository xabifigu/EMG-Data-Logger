import serial
import time
import numpy as np
from multiprocessing import Queue
import os

###################
# SERIAL COM
###################
def serialConfig (serialPort, bauds):
  """ 
  @def Iniciar y configurar el puerto serie
  @arg none
  @return objeto de puerto serie
  """
  s = serial.Serial()
  s.baudrate = bauds
  s.port = serialPort
  s.timeout = 1
  return s

###########################
# FUNCIONES TRATA DE DATOS
##########################
#
def getHighNibbleFromByte(data):
  """ 
  @def 
  @arg 
  @return 
  """
  x = data & 0xF0
  return (x >> 4)

#
def getLowNibbleFromByte(data):
  """ 
  @def 
  @arg 
  @return 
  """
  return (data & 0x0F)

#
def  bytes2Word(highByte, lowByte):
  """ 
  @def 
  @arg 
  @return 
  """
  x = highByte << 8
  return (x | lowByte)


##################
# MAIN
##################
class SerialCom():

  MAX_CHANNELS = 8
  DATA_BUFFER_SIZE = 1

  def __init__(self, name, q, 
              nChannels=8, nCh2Show=1, 
              comPort='COM7', bauds=9600,
              outFolder='.\\', vMax=4095, rGain=201000):

    self.q = q
    self.nChannels = nChannels
    self.nCh2Show = nCh2Show
    self.comPort = comPort
    self.bauds = bauds
    self.outFolder = outFolder
    self.vMax = vMax
    # self.vMin = vMin
    self.gain = 201 * rGain / 1000

    print (time.time())

    # inicializar y abrir puerto serie
    ser = serialConfig(self.comPort, self.bauds)

    # tiempo entre cada dato: 
    # tiempo entre cada bit = 1/baudrate
    # número de bit por dato = 10
    # Dato en milisegundos
    newDataPeriod_ms = ((1 / ser.baudrate) * 10) * 1000

    isSerialOpen = False
    try:
      ser.open()
      isSerialOpen = True
    except:
      print('Error abriendo puerto serie')  # @note traza

    # OBTENER DATOS
    # obetener datos del puerto serie hasta que no se reciban más datos

    numReadData = 0

    t_start = time.time()

     # sincronizar datos del puerto serie
    # Se busca leer el número de canal de manera consecutiva
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
        # si no se leyó ningún dato, se acaba el bucle
        if len(x) < 1:
          isSerialOpen = False
          break
        if dataWithCh is True:
          # Se espera que el dato leído contenga número de canal
          numberOfCh = getHighNibbleFromByte(ord(x))
          if numberOfCh == 0:
            # Todavía no se ha leído un canal válido,
            # por lo que el primer canal leído, será el canal esperado
            nextCh = numberOfCh
          # El canal es válido sólo si es un número válido,
          # y es el canal esperado
          if numberOfCh < self.MAX_CHANNELS and numberOfCh == nextCh:
            dataWithCh = False  # No se espera canal en el siguiente dato
            numberReadCh += 1   # Se incrementa el número de canales leídos
            if nextCh == (self.MAX_CHANNELS-1):
              nextCh = 0
            else:
              nextCh = numberOfCh+1
            print ('Correcto: ' + str(numberOfCh)) # @note traza
          else:
            # no se ha leído un número válido, resetear contador
            numberReadCh = 0
            print('Canal no válido: ' + str(numberOfCh))  # @note traza
        else:
          # En el siguiente dato se espera leer canal
          dataWithCh = True
          print('Canal no esperado')  # @note traza

    if isSerialOpen is True:
      # crear matrices para almacenar los datos
      matrixCh = [[0 for x in range(1)] for y in range(self.MAX_CHANNELS)]
      matrixTime = [[0 for x in range(1)] for y in range(self.MAX_CHANNELS)]

      # el primer byte no es canal
      x = ser.read()
      cnt = 0   # @note traza
      cntCh0 = 0
      numReadData = 0
      while True:
        # Los datos se leen de dos en dos bytes:
        #   1. byte: ch + data
        #   2. byte: data
        arr = ser.read(2)
        # si no se leen datos, se acaba el bucle
        if len(arr) < 2:
          print ("No more data")
          break
        else:
          # Se procesan los datos recibidos para obtener
          # el número de canal y el valor correspondiente
          timeData = newDataPeriod_ms*numReadData
          numReadData += 2
          chNum, adcValue = self.getProcessReadData(arr)

          # si es un canal correcto, se almacena
          if chNum < self.MAX_CHANNELS:
            matrixCh[chNum].append(adcValue)
            matrixTime[chNum].append(timeData)

          dataToSend = [timeData,adcValue]

          if chNum < self.nCh2Show:
            if self.q[chNum].empty():
              self.q[chNum].put(dataToSend)

          # @note traza
          cnt += 1 
          print("Serial: " + str(cnt) + " Ch0: " + str(cntCh0))

    # se paran todas las colas ('Nono' es el comando para parar)
    for i in range (0, self.nCh2Show):
      self.q[i].put(None)


    if not (ser.closed):
      ser.close()
      
    # @note traza
    print ("Data received")
    print ("Número de datos: " + str(numReadData/2))

    # PROCESAR DATOS
    if (numReadData != 0):      
      # se elimina el primer dato de cada matriz 
      # (primer elemento usado para creación de matriz)
      for i in range (0, self.MAX_CHANNELS):
        del matrixCh[i][0]
        del matrixTime[i][0]

    # GUARDAR LOS DATOS
    # los datos se guardan en CSV:
    # Columna 0: tiempo
    # Columna 1: valores ADC
    if (numReadData != 0):
      timeString = time.strftime("%Y%m%d%H%M%S")
      pathName = self.outFolder + '\\' + timeString
      if not os.path.exists(pathName): 
        os.makedirs(pathName)
      for i in range (0, self.nChannels):
        M = np.asarray([ matrixTime[i], matrixCh[i] ])
        MT = np.transpose(M)
        fileName = pathName + '\\' + timeString  \
                  + "_emg_ch" + str(i) + ".emgdat"
        np.savetxt(fileName, MT, delimiter=",")

    # @note traza
    t_elapsed = time.time() - t_start
    print(t_elapsed)

    #
  def getProcessReadData(self, arData):
    """ 
    @def 
    @arg 
    @return 
    """
    ch = getHighNibbleFromByte(arData[0])
    aux = getLowNibbleFromByte(arData[0])
    value = bytes2Word(aux,arData[1])
    value = (value * self.vMax / 4095 ) / self.gain
    return ch, value


def main():
    q = []
    q.append(Queue())
    q[0].put(None)
    serialCom = SerialCom('Serial-1', q)
    return 0

if __name__ == '__main__':
    main()