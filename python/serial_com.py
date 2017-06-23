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
  s.timeout = 10
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

t_start = time.time()
print (t_start)

# inicializar y abrir puerto serie
ser = serialConfig()
ser.open()

# obetener datos del puerto serie hasta que no se reciban más datos
arSerialData = [0]
arTime = [0]

while True:
  x = ser.read(255)
  if len(x) < 255:
    if len(x) != 0:
      arSerialData = np.concatenate((arSerialData,x))
    else:
      pass
    print ("No more data")
    break
  else:
    arSerialData = np.concatenate((arSerialData,x))

if not (ser.closed):
  ser.close()
  
print ("Data received")

# Procesar datos
F = openNewFileW()
F.write(str(arSerialData))

if not (F.closed):
  F.close()


t_elapsed = time.time() - t_start
print(t_elapsed)
# print(process_time())