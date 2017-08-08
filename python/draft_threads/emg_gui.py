# !/usr/bin/env python

import os
from tkinter import *
from tkinter import ttk, font
from serial.tools import list_ports
from tkinter import filedialog

import time

from threading import Thread
from multiprocessing import Queue

# from serial_com import SerialCom
# from emgPlot import SetPlot
from emgThreads import ThreadsApp

# Gestor de geometría (grid)

class App():
    def __init__(self):
        self.root = Tk()
        self.root.title("EMG Data Logger")
        # self.root.wm_iconbitmap(r'Upv-ehu.ico')
        self.root.minsize(175,75)
        self.root.resizable(width=False,height=False)
        
        # Cambia el formato de la fuente actual a negrita para
        # resaltar las dos etiquetas que acompañan a las cajas
        # de entrada. (Para este cambio se ha importado el  
        # módulo 'font' al comienzo del programa):
        fuente = font.Font(weight='bold')
        
        # Define los difrentes frames
        self.topFrame = ttk.Frame(self.root, borderwidth=2,
                               relief="raised", padding=(10,10))
        self.bottomFrame = ttk.Frame(self.root)
        self.msgFrame = ttk.Frame (self.root,borderwidth=1,
                               relief="sunken")

        # define las etiquetas
        self.labPorts = ttk.Label(self.topFrame, text="COM:", padding=(5,5))
        self.labBauds = ttk.Label(self.topFrame, text='Bauds:', padding=(5,5))
        self.labComConfig = ttk.Label(self.topFrame, text='Stopbit:1 / Parity:0', padding=(5,5))
        self.labOutput = ttk.Label(self.topFrame, text='Output Folder', padding=(2,0))
        self.labMaxChls = ttk.Label(self.topFrame, text='ADC channels: ')
        self.labNmChToShow = ttk.Label(self.topFrame, text='Channels to show')
        self.labMsg = ttk.Label(self.msgFrame, text='Stopped')

        # definición de Combobox
        self.portsList = StringVar()
        self.cbPort = ttk.Combobox(self.topFrame, textvariable=self.portsList,
                                    width=10)
        
        # definici󮠤e entrada de texto
        self.Bauds = StringVar()
        self.etBauds = ttk.Entry(self.topFrame, textvariable=self.Bauds,
                                width=10)
        self.Bauds.set("9600")

        self.Folder = StringVar()
        self.etFolder = ttk.Entry(self.topFrame, textvariable=self.Folder)

        self.NmMaxCh = StringVar()
        self.etNmMaxCh = ttk.Entry(self.topFrame, textvariable=self.NmMaxCh,
                                width=2)
        self.NmMaxCh.set("8")

        self.NmChlShow = StringVar()
        self.etNmChl = ttk.Entry(self.topFrame, textvariable=self.NmChlShow,
                                width=2)
        self.NmChlShow.set("1")

        # definir separador
        self.separ1 = ttk.Separator(self.topFrame, orient=HORIZONTAL)
        self.separ2 = ttk.Separator(self.topFrame, orient=HORIZONTAL)
        
        # definición de botones
        self.btStartText = StringVar()
        self.btStart = ttk.Button(self.bottomFrame, textvariable=self.btStartText, 
                                 padding=(5,5), command=self.start)
        self.btStartText.set("Start")
        self.btExit = ttk.Button(self.bottomFrame, text="Exit", 
                                 padding=(5,5), command=quit)
        self.btRefresh = ttk.Button(self.topFrame, text="Refresh", 
                                 padding=(2,2), command=self.actualizarPuertos)

        self.btOpenFolder = ttk.Button(self.topFrame, text="Select", 
                                    padding=(2,2), command=self.selectOutputFolder)
                                 
        # Se definen las posiciones de los widgets dentro de
        # la ventana.
        self.topFrame.grid(column=0, row=0, padx=5, pady=5)
        self.bottomFrame.grid(column=0, row=1, padx=5, pady=5)
        self.msgFrame.grid(column=0, row=3, columnspan=4, sticky=W+E)

        self.labPorts.grid(column=0, row=0, padx=5, pady=5)
        self.cbPort.grid(column=1, row=0, columnspan=2, padx=5, pady=5)
        self.btRefresh.grid(column=3, row=0, columnspan=2, padx=5, pady=5)

        self.labBauds.grid(column=0, row=1, padx=5, pady=5)
        self.etBauds.grid(column=1, row=1, padx=5, columnspan=2, pady=5, sticky=W)
        self.labComConfig.grid(column=3, row=1, padx=5, columnspan=2, pady=5, sticky=W)

        self.separ1.grid(column=0, row=2, columnspan=5, padx=5, pady=5, sticky=W+E)

        self.labMaxChls.grid(column=0, row=3, padx=5, pady=5, columnspan=2)
        self.etNmMaxCh.grid(column=2, row=3, padx=5, pady=5, sticky=W)
        self.labNmChToShow.grid(column=0, row=4, padx=5, pady=5, columnspan=2)
        self.etNmChl.grid(column=2, row=4, padx=5, pady=5, sticky=W)

        self.separ2.grid(column=0, row=5, columnspan=5, padx=5, pady=5, sticky=W+E)

        self.labOutput.grid(column=0, row=6, padx=2, pady=0, columnspan=3, sticky=W)
        self.etFolder.grid(column=0, row=7, padx=2, pady=0, columnspan=4, sticky=W+E)
        self.btOpenFolder.grid(column=4, row=7, padx=2, pady=0)

        self.btStart.grid(column=1, row=0, padx=5, pady=5)
        self.btExit.grid(column=2, row=0, padx=5, pady=5)

        # frame para mensaje
        self.labMsg.grid(column=0, row=0, columnspan=4, padx=1, pady=1, sticky=W)

        # actualizar puertos (combobox)
        self.actualizarPuertos()

        
        # Se inicia el gui
        
        self.root.mainloop()
    
    # El método start es quien lanza el script de captura de datos  
    def start(self):
        if self.btStartText.get() == "Start":
            if self.checkConsistency() == True:
                print(self.cbPort.get())
                self.btStartText.set("Stop")
                self.setInfoMsg("Running")
                try:
                    iBauds = int(self.Bauds.get())
                    iMaxCh = int(self.NmMaxCh.get())
                    iCh2Show = int(self.NmChlShow.get())
                    # SerialCom(comPort=self.cbPort.get(), bauds=iBauds)
                    runPlot = ThreadsApp(nChannels=iMaxCh, nCh2Show=iCh2Show,
                                        comPort=self.cbPort.get(), bauds=iBauds,
                                        outFolder=self.etFolder.get())
                except:
                    self.setErrorMsg("ERROR: Bauds not valid!")
        elif self.btStartText.get() == "Stop":
            self.btStartText.set("Start")
            self.setInfoMsg("Stopped")
        else:
            pass

    def checkConsistency(self):
        ret = False
        if self.cbPort.get() == "" or \
           self.etBauds.get() == "" or \
           self.etFolder.get() == "" or \
           self.etNmMaxCh.get() == "" or \
           self.etNmChl.get() == "":
            print("Some settings are empty!")
            self.setErrorMsg("ERROR: Some settings are empty!")
        elif self.etNmMaxCh.get() < self.etNmChl.get():
            print("Number of channles to show bigger than number of channels")
            self.setErrorMsg("ERROR: Number of channels are not correct")
        else:
            ret = True
        return ret

    # actualiza la lista de puertos COM
    def actualizarPuertos(self):
        self.cbPort.set('')
        ports = list_ports.comports()
        listPorts = [None]
        count = 0
        # obtener primera palabra de cada string
        for i in ports:
          listPorts.append(str(ports[count]).split(' ', 1)[0])
          count += 1
        del listPorts[0]
        self.cbPort['values'] = listPorts
        self.cbPort.set(listPorts[0])

    # selección de carpeta de salida de ficheros
    def selectOutputFolder(self):
        print("Output Folder")
        # self.root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
        #                                    filetypes=[("Text Files", "*.txt")])
        self.Folder.set(filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory"))

    # inserta un mensaje de error
    def setErrorMsg(self, text):
        self.labMsg['text'] = text
        self.labMsg['foreground'] = "red"

    # inserta un mensaje de información
    def setInfoMsg(self, text):
        self.labMsg['text'] = text
        self.labMsg['foreground'] = "black"
    
    # inserta un mesaje de precaución
    def setWarningMsg(self, text):
        self.labMsg['text'] = text
        self.labMsg['foreground'] = "yellow"

# main
def main():
    mi_app = App()
    return 0

if __name__ == '__main__':
    main()