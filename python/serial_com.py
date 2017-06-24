import serial
import binascii
import time
import numpy as np

###################
# SERIAL COM
###################
def serialConfig ():
  s = serial.Serial()
  s.baudrate = 115200
  s.port = 'COM5'
  s.timeout = 1
  return s

#######################
# GESTIÓN DE FICHEROS
#######################
def openNewFileW ():
  newFile = open ("serial_data.txt", "w")
  return newFile

###########################
# FUNCIONES TRATA DE DATOS
##########################


##################
# MAIN
##################
# constantes
MAX_CHANNELS = 8
DATA_BUFFER_SIZE = 1

print (time.time())

# inicializar y abrir puerto serie
ser = serialConfig()

# tiempo entre cada dato: 
# tiempo entre cada bit = 1/baudrate
# número de bit por dato = 10
newDataPeriod = (1 / ser.baudrate) * 10

ser.open()

# OBTENER DATOS
# obetener datos del puerto serie hasta que no se reciban más datos
arSerialData = [0]
arTime = [0]
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
      arTime.append(time.time() - t_start)
      arSerialData.append(ord(x))
      numReadData = numReadData + len(x)
    else:
      pass
    print ("No more data")
    break
  else:
    arTime.append(newDataPeriod*numReadData)
    arSerialData.append(ord(x))
    numReadData = numReadData + DATA_BUFFER_SIZE

if not (ser.closed):
  ser.close()
  
print ("Data received")
print ("Número de datos: " + str(len(arSerialData)))

# PROCESAR DATOS

# GUARDAR LOS DATOS
F = openNewFileW()
F.write(str(arSerialData))

if not (F.closed):
  F.close()


t_elapsed = time.time() - t_start
print(t_elapsed)
# print(process_time())