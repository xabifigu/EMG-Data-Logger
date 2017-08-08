import serial
# import binascii
import time
import numpy as np
import matplotlib.pyplot as plt

# constantes globales
MAX_CHANNELS = 8
DATA_BUFFER_SIZE = 1

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
  # s.port = 'COM7'
  s.timeout = 1
  return s

#######################
# GESTIÓN DE FICHEROS
#######################
def openNewFileW ():
  """ 
  @def 
  @arg 
  @return 
  """
  newFile = open ("serial_data.txt", "w")
  return newFile

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

#
def getProcessReadData(arData):
  """ 
  @def 
  @arg 
  @return 
  """
  ch = getHighNibbleFromByte(arData[0])

  aux = getLowNibbleFromByte(arData[0])
  value = bytes2Word(aux,arData[1])
  return ch, value

#
def getNextExpectedCh (nextCh):
  """ 
  @def 
  @arg 
  @return 
  """
  global MAX_CHANNELS

  if (nextCh == (MAX_CHANNELS-1)):
    nextCh = 0
  else:
    nextCh += 1
  return nextCh

#
def searchHeader (arData):
  """ 
  @def 
  @arg 
  @return 
  """
  # Formato de datos lo componen dos bytes XY0 Y1Y2
  # X = número de canal (4 bits)
  # Y0Y1Y2 = dato del canal (12 bits)
  # Primero hay que determinar qué bytes contienen la 
  # cabecera de cada canal: pares o impares 

  global MAX_CHANNELS

  NM_CH_TO_BE_READ = MAX_CHANNELS*2
  startByte = -1
  headersFound = False
  index = 0
  expectedCh = 0
  chCounter = 0
  startSearch = False

  # Bucle para encontrar el patrón correcto
  # Se ejecutará hasta leer en el orden correcto todos los canales dos veces,
  # o hasta que se hayan leído 50 bytes sin encontrar la cabecera 
  while ((chCounter < NM_CH_TO_BE_READ) and (index <= 50)):
    while (startSearch != True):
      expectedCh = getHighNibbleFromByte(arData[index])
      if (expectedCh < MAX_CHANNELS):
        # posible canal encontrado
        startSearch = True
        startByte = index   # se guarda el primer dato del cual hay que empezar a leer
        # se almacena el siguiente canal que se espera encontrar
        expectedCh = getNextExpectedCh (expectedCh)

        index += 2      # se incrementa el índice en dos (se busca cabecera/num canal)
        chCounter += 1  # se incrementa el contados de cabeceras encontradas
      else:
        # posible canal no encontrado, comprobar siguiente byte
        index += 1
    
    # Bucle hasta encontrar todas las cabeceras esperadas o encontrar un error
    while ((chCounter < (NM_CH_TO_BE_READ)) and (chCounter != 0)):
      if (expectedCh == getHighNibbleFromByte(arData[index])):
        # el canal encontrado es el esperado
        index += 2      # se incrementa el índice en dos (se busca cabecera/num canal)
        chCounter += 1  # se incrementa el contados de cabeceras encontradas 
        # se almacena el siguinte canal que se espera encontrar
        expectedCh = getNextExpectedCh (expectedCh)
      else:
        # se ha detectado un error en la trama
        # se resetean el contador y se decrementa el índice, ya que el
        # byte correcto puede haberse saltado
        expectedCh = 0
        chCounter = 0
        index -= 1
        startSearch = False

  if (chCounter >= NM_CH_TO_BE_READ):
    print ('Patron correcto!')
  else:
    print ('Patron no encontrado')
    startByte = -1
  
  return startByte


##################
# MAIN
##################
class SerialCom():

  MAX_CHANNELS = 8
  DATA_BUFFER_SIZE = 1

  def __init__(self, name, q, nChannels=1, comPort='COM8', bauds=9600):
      
    print (time.time())

    # inicializar y abrir puerto serie
    ser = serialConfig(comPort, bauds)

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
      print('Error abriendo puerto serie')

    # OBTENER DATOS
    # obetener datos del puerto serie hasta que no se reciban más datos

    # arSerialData = [None]
    # arTime = [None]
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
          else:
            pass
          # El canal es válido sólo si es un número válido,
          # y es el canal esperado
          if numberOfCh < self.MAX_CHANNELS and numberOfCh == nextCh:
            dataWithCh = False  # No se espera canal en el siguiente dato
            numberReadCh += 1   # Se incrementa el número de canales leídos
            if nextCh == (self.MAX_CHANNELS-1):
              nextCh = 0
            else:
              nextCh = numberOfCh+1
            print ('Correcto: ' + str(numberOfCh))
          else:
            # no se ha leído un número válido, resetear contador
            numberReadCh = 0
            print('Canal no válido: ' + str(numberOfCh))
        else:
          # En el siguiente dato se espera leer canal
          dataWithCh = True
          print('Canal no esperado')
    else:
      pass

    if isSerialOpen is True:
      # crear matrices para almacenar los datos
      matrixCh = [[0 for x in range(1)] for y in range(MAX_CHANNELS)]
      matrixTime = [[0 for x in range(1)] for y in range(MAX_CHANNELS)]

      # el primer byte no es canal
      x = ser.read()
      cnt = 0
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
          chNum, adcValue = getProcessReadData(arr)

          if chNum < MAX_CHANNELS:
            matrixCh[chNum].append(adcValue)
            matrixTime[chNum].append(timeData)
          else:
            pass

          dataToSend = [timeData,adcValue]

          # if chNum == 0:
          #   if q.empty():
          #     # q.put(adcValue)
          #     q.put(dataToSend)
          #   cntCh0 += 1
          # else:
          #   pass   

          # if chNum == 0:
          #   if q[0].empty():
          #     # q.put(adcValue)
          #     q[0].put(dataToSend)
          #   cntCh0 += 1
          # else:
          #   pass  

          # if chNum == 1:
          #   if q[1].empty():
          #     # q.put(adcValue)
          #     q[1].put(dataToSend)
          # else:
          #   pass   

          if chNum < nChannels:
            if q[chNum].empty():
              # q.put(adcValue)
              q[chNum].put(dataToSend)
            # cntCh0 += 1
            else:
              pass  
          else:
            pass

          cnt += 1 
          print("Serial: " + str(cnt) + " Ch0: " + str(cntCh0))
          
      # q.put(None) 
    else:
      pass

    # q.put(None)
    # q[0].put(None)
    # q[1].put(None)

    for i in range (0, nChannels):
      q[i].put(None)



    # while True:
    #   x = ser.read(DATA_BUFFER_SIZE)
    #   if len(x) < DATA_BUFFER_SIZE:
    #     if len(x) != 0:
    #       arTime.append(newDataPeriod_ms*numReadData)
    #       arSerialData.append(ord(x))
    #       numReadData = numReadData + len(x)
    #     else:
    #       pass
    #     print ("No more data")
    #     break
    #   else:
    #     arTime.append(newDataPeriod_ms*numReadData)
    #     arSerialData.append(ord(x))
    #     numReadData += DATA_BUFFER_SIZE

    # if not (ser.closed):
    #   ser.close()
      
    print ("Data received")
    print ("Número de datos: " + str(numReadData/2))

    # PROCESAR DATOS
    if (numReadData != 0):
      # # eliminar el primer item del array, ya que no es válido
      # del arSerialData[0]
      # del arTime[0]
      # # obtener el primer byte válido
      # startByte = searchHeader(arSerialData)
      # # separa los datos según el canal leído
      # index = startByte
      # # crear matrices para almacenar los datos
      # matrixCh = [[0 for x in range(1)] for y in range(MAX_CHANNELS)]
      # matrixTime = [[0 for x in range(1)] for y in range(MAX_CHANNELS)]
      # while (index < (numReadData-1)):
      #   # recoger datos
      #   currentData = arSerialData[index:index+2]
      #   chNum, adcValue = getProcessReadData(currentData)

      #   # comprobar que se leído un canal correcto
      #   # La matriz se creó antes de ser usada, por lo que las columnas ya
      #   # tienen un elemento.
      #   # Los siguientes datos se guardan usando 'append'
      #   if chNum < MAX_CHANNELS:
      #     matrixCh[chNum].append(adcValue)
      #     matrixTime[chNum].append(arTime[index])
      #     index += 2
      #   else:
      #     # el canal leído no es correcto.
      #     # puede que la lectura se haya desincronizado, por lo que
      #     # se vuelve a buscar dato correcto: se apunta directamente al
      #     # siguiente elemento de la lista
      #     index += 1
      #     pass

      
      # se elimina el primer dato de cada matriz 
      # (primer elemento usado para creación de matriz)
      for i in range (0, MAX_CHANNELS):
        del matrixCh[i][0]
        del matrixTime[i][0]

    else:
      pass


    # GUARDAR LOS DATOS
    # los datos se guardan en CSV:
    # Columna 0: tiempo
    # Columna 1: valores ADC
    if (numReadData != 0):
      for i in range (0, MAX_CHANNELS):
        M = np.asarray([ matrixTime[i], matrixCh[i] ])
        MT = np.transpose(M)
        fileName = "data_channel_" + str(i) + ".csv"
        np.savetxt(fileName, MT, delimiter=",")
    else:
      pass

    # # MOSTRAR DATOS
    # # mostrar gráfica de los datos obtenidos, siempre y cuando se haya
    # # recibido al menos un dato
    # if (numReadData != 0):
    #   for i in range (0, MAX_CHANNELS):
    #     fig = plt.figure(i)
    #     plt.plot(matrixTime[i],matrixCh[i])
    #     title = 'Channel ' + str(i) 
    #     fig.suptitle(title, fontsize=18)
    #     plt.xlabel('time (ms)')
    #     plt.ylabel('value')
    #   plt.show()
    # else:
    #   pass


    t_elapsed = time.time() - t_start
    print(t_elapsed)
    # print(process_time())

def main():
    serialCom = SerialCom('Serial-1', None, 2, comPort='COM8', bauds=9600)
    return 0

if __name__ == '__main__':
    main()