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
def serialConfig (serialPort):
  """ 
  @def Iniciar y configurar el puerto serie
  @arg none
  @return objeto de puerto serie
  """
  s = serial.Serial()
  s.baudrate = 9200
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

  def __init__(self, comPort='COM7'):
      
    print (time.time())

    # inicializar y abrir puerto serie
    ser = serialConfig(comPort)

    # tiempo entre cada dato: 
    # tiempo entre cada bit = 1/baudrate
    # número de bit por dato = 10
    # Dato en milisegundos
    newDataPeriod_ms = ((1 / ser.baudrate) * 10) * 1000

    try:
      ser.open()
    except:
      print('Error abriendo puerto serie')

    # OBTENER DATOS
    # obetener datos del puerto serie hasta que no se reciban más datos
    arSerialData = [None]
    arTime = [None]
    numReadData = 0

    t_start = time.time()

    # while True:
    #   x = ser.read(255)
    #   y = ord(x)
    #   if len(x) < 255:
    #     if len(x) != 0:
    #       arSerialData = np.concatenate((arSerialData,x))
    #     else:
    #       pass
    #     print ("No more data")
    #     break
    #   else:
    #     arSerialData = np.concatenate((arSerialData,x))

    while True:
      x = ser.read(DATA_BUFFER_SIZE)
      if len(x) < DATA_BUFFER_SIZE:
        if len(x) != 0:
          arTime.append(newDataPeriod_ms*numReadData)
          arSerialData.append(ord(x))
          numReadData = numReadData + len(x)
        else:
          pass
        print ("No more data")
        break
      else:
        arTime.append(newDataPeriod_ms*numReadData)
        arSerialData.append(ord(x))
        numReadData += DATA_BUFFER_SIZE

    if not (ser.closed):
      ser.close()
      
    print ("Data received")
    print ("Número de datos: " + str(len(arSerialData)-1))

    # PROCESAR DATOS
    if (numReadData != 0):
      # eliminar el primer item del array, ya que no es válido
      del arSerialData[0]
      del arTime[0]
      # obtener el primer byte válido
      startByte = searchHeader(arSerialData)
      # separa los datos según el canal leído
      index = startByte
      # crear matrices para almacenar los datos
      matrixCh = [[0 for x in range(1)] for y in range(MAX_CHANNELS)]
      matrixTime = [[0 for x in range(1)] for y in range(MAX_CHANNELS)]
      while (index < (numReadData-1)):
        # recoger datos
        currentData = arSerialData[index:index+2]
        chNum, adcValue = getProcessReadData(currentData)

        # comprobar que se leído un canal correcto
        # La matriz se creó antes de ser usada, por lo que las columnas ya
        # tienen un elemento.
        # Los siguientes datos se guardan usando 'append'
        if chNum < MAX_CHANNELS:
          matrixCh[chNum].append(adcValue)
          matrixTime[chNum].append(arTime[index])
          index += 2
        else:
          # el canal leído no es correcto.
          # puede que la lectura se haya desincronizado, por lo que
          # se vuelve a buscar dato correcto: se apunta directamente al
          # siguiente elemento de la lista
          index += 1
          pass

      
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

    # F = openNewFileW()
    # F.write(str(arSerialData))
    # if not (F.closed):
    #   F.close()

    # MOSTRAR DATOS
    # mostrar gráfica de los datos obtenidos, siempre y cuando se haya
    # recibido al menos un dato
    if (numReadData != 0):
      for i in range (0, MAX_CHANNELS):
        fig = plt.figure(i)
        plt.plot(matrixTime[i],matrixCh[i])
        title = 'Channel ' + str(i) 
        fig.suptitle(title, fontsize=18)
        plt.xlabel('time (ms)')
        plt.ylabel('value')
      plt.show()



      # # Three subplots sharing both x/y axes
      # f, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8) = plt.subplots(8, sharex=True, sharey=True)
      # # x = matrixTime[1]
      # ax1.plot(matrixTime[0], matrixCh[0])
      # ax1.set_title('Sharing both axes')
      # ax2.scatter(matrixTime[1], matrixCh[1])
      # ax3.scatter(matrixTime[2], matrixCh[2], color='r')
      # ax4.scatter(matrixTime[3], matrixCh[3], color='g')
      # ax5.scatter(matrixTime[4], matrixCh[4])
      # ax6.scatter(matrixTime[5], matrixCh[5], color='r')
      # ax7.scatter(matrixTime[6], matrixCh[6], color='g')
      # ax8.scatter(matrixTime[7], matrixCh[7])

      # # Fine-tune figure; make subplots close to each other and hide x ticks for
      # # all but bottom plot.
      # f.subplots_adjust(hspace=0)
      # plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
      # plt.show()

    else:
      pass


    t_elapsed = time.time() - t_start
    print(t_elapsed)
    # print(process_time())

def main():
    serialCom = SerialCom()
    return 0

if __name__ == '__main__':
    main()