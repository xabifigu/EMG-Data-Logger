# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
# comprobación de que ejecuta bajo la versión correcta de Python
req_version = (3,5)
if sys.version_info < req_version:
    raise SyntaxError ("Python v.3.5 or bigger is needed. Please update it.")

import os
from tkinter import *
from tkinter import ttk, font
from serial.tools import list_ports
from tkinter import filedialog
import tkinter as tk

from runemg import csv2Plot

# Gestor de geometría
class MainWindow(tk.Frame):
    """
    Clase de la ventana principal
    """
    def __init__(self, *args, **kwargs):
        """ 
        Método inicial de la clase para crear todos los objetos de la ventana
        """
        tk.Frame.__init__(self, *args, **kwargs)        
        # Define los difrentes frames
        self.topFrame = ttk.Frame(self, borderwidth=2,
                               relief="raised", padding=(10,10))
        self.bottomFrame = ttk.Frame(self)
        self.msgFrame = ttk.Frame (self,borderwidth=1,
                               relief="sunken")

        # define las etiquetas
        self.labPorts = ttk.Label(self.topFrame, text="COM:", padding=(5,5))
        self.labBauds = ttk.Label(self.topFrame, text='Bauds:', padding=(5,5))
        self.labComConfig = ttk.Label(self.topFrame, text='Stopbit: 1 / Parity: 0', padding=(5,5))
        self.labOutput = ttk.Label(self.topFrame, text='Output Folder', padding=(2,0))
        self.labMaxChls = ttk.Label(self.topFrame, text='Active channels')
        self.labNmChToShow = ttk.Label(self.topFrame, text='RT channels')
        self.labVmax= ttk.Label(self.topFrame, text='Vcc (v)')
        self.labRgain= ttk.Label(self.topFrame, text='Rgain (ohm)')
        self.labMsg = ttk.Label(self.msgFrame, text='Active')

        # definición de Combobox
        self.portsList = StringVar()
        self.cbPort = ttk.Combobox(self.topFrame, textvariable=self.portsList,
                                    width=10)
        
        # definiciones entrada de texto
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

        self.vMax = StringVar()
        self.etVmax = ttk.Entry(self.topFrame, textvariable=self.vMax,
                                width=6)
        
        self.rGain = StringVar()
        self.etRgain = ttk.Entry(self.topFrame, textvariable=self.rGain,
                                width=6)

        # definir separador
        self.separ1 = ttk.Separator(self.topFrame, orient=HORIZONTAL)
        self.separ2 = ttk.Separator(self.topFrame, orient=HORIZONTAL)
        self.separ3 = ttk.Separator(self.topFrame, orient=HORIZONTAL)
        
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
 
        self.btShowGraph = ttk.Button(self.topFrame, text="Show Graphs From Directory", 
                            padding=(2,2), command=self.showGraphs)
														
        # Se definen las posiciones de los widgets dentro de la ventana.
        self.topFrame.grid(column=0, row=0, padx=5, pady=5)
        self.bottomFrame.grid(column=0, row=1, padx=5, pady=5)
        self.msgFrame.grid(column=0, row=3, columnspan=4, sticky=W+E)

        self.labMaxChls.grid(column=0, row=0, padx=5, pady=5, columnspan=2)
        self.etNmMaxCh.grid(column=2, row=0, padx=5, pady=5, sticky=W)
        self.labNmChToShow.grid(column=0, row=1, padx=5, pady=5, columnspan=2)
        self.etNmChl.grid(column=2, row=1, padx=5, pady=5, sticky=W)
        self.labVmax.grid(column=3, row=0, padx=5, pady=5, sticky=E)
        self.etVmax.grid(column=4, row=0, padx=5, pady=5, sticky=W)
        self.labRgain.grid(column=3, row=1, padx=5, pady=5, sticky=E)
        self.etRgain.grid(column=4, row=1, padx=5, pady=5, sticky=W)

        self.separ1.grid(column=0, row=2, columnspan=5, padx=5, pady=5, sticky=W+E)

        self.labPorts.grid(column=0, row=3, padx=5, pady=5)
        self.cbPort.grid(column=1, row=3, columnspan=2, padx=5, pady=5)
        self.btRefresh.grid(column=3, row=3, columnspan=2, padx=5, pady=5, sticky=W)

        self.labBauds.grid(column=0, row=4, padx=5, pady=5)
        self.etBauds.grid(column=1, row=4, padx=5, columnspan=2, pady=5, sticky=W)
        self.labComConfig.grid(column=3, row=4, padx=5, columnspan=2, pady=5, sticky=W)

        self.separ2.grid(column=0, row=5, columnspan=5, padx=5, pady=5, sticky=W+E)

        self.labOutput.grid(column=0, row=6, padx=2, pady=0, columnspan=3, sticky=W)
        self.etFolder.grid(column=0, row=7, padx=2, pady=0, columnspan=4, sticky=W+E)
        self.btOpenFolder.grid(column=4, row=7, padx=2, pady=0)

        self.btShowGraph.grid(column=0, row=8, columnspan=5, padx=5, pady=5, sticky=W+E)

        self.separ3.grid(column=0, row=9, columnspan=5, padx=5, pady=5, sticky=W+E)

        self.btStart.grid(column=1, row=0, padx=5, pady=5)
        self.btExit.grid(column=2, row=0, padx=5, pady=5)

        # frame para mensaje
        self.labMsg.grid(column=0, row=0, columnspan=4, padx=1, pady=1, sticky=W)

        # actualizar puertos (combobox)
        self.actualizarPuertos()
    
    def start(self):
        """ 
        @def    Lanza el script de captura de datos
        @arg    none
        @return none
        """
        # se comprueba la consistencia de datos antes de ejecutar el script
        if self.checkConsistency() == True: 
            # print(self.cbPort.get())	# @note traza
            self.setInfoMsg("Active")
            try:
                if self.rGain.get() is "":
                    self.rGain.set("0")
                if self.vMax.get() is "":
                    self.vMax.set("0")
                
                cmdArgs = self.NmMaxCh.get() + " " + self.NmChlShow.get() + " " + self.cbPort.get() + \
                            " " + self.Bauds.get() + " " + self.etFolder.get().replace('/','\\') + \
                            " " + self.vMax.get() + " " + self.rGain.get()
                os.system("runemg.py " + cmdArgs)
            except:
                self.setErrorMsg("ERROR: Something is wrong.")

    def checkConsistency(self):
        """ 
        @def    Se comprueba que los datos introducidos son correctos
        @arg    none
        @return True si todo es correcto
                False si algún dato no es válido
        """
        # se comprueba la consistencia de los datos
        ret = False
        if self.cbPort.get() == "" or \
           self.etBauds.get() == "" or \
           self.etFolder.get() == "" or \
           self.etNmMaxCh.get() == "" or \
           self.etNmChl.get() == "":
            # print("Some settings are empty!")   # @note traza
            self.setErrorMsg("ERROR: Some settings are empty!")
        elif int(self.etNmMaxCh.get()) > 8 or int(self.etNmChl.get()) > 8:
            # print("Number of channles bigger than 8")  # @note traza
            self.setErrorMsg("ERROR: Number of channels cannot be bigger than 8")    
        elif int(self.etNmMaxCh.get()) < 1 or int(self.etNmChl.get()) < 1:
            # print("Number of channles lower than 1")  # @note traza
            self.setErrorMsg("ERROR: Number of channels cannot be less than 1")      
        elif int(self.etNmMaxCh.get()) < int(self.etNmChl.get()):
            # print("Number of channles to show bigger than number of channels to save")  # @note traza
            self.setWarningMsg("WARNING: Number of channels are not correct")     
        else:
            ret = True
        return ret

    # actualiza la lista de puertos COM
    def actualizarPuertos(self):
        """ 
        @def    Actualizar lista de puertos serie disponibles
        @arg    none
        @return none
        """
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
        if listPorts:
            self.cbPort.set(listPorts[0])

    def showGraphs(self):
        """ 
        @def    Mostrar gráficos desde ficheros
        @arg    none
        @return none
        """
        # print("mostrar diagramas")  # @note traza
        direct = filedialog.askdirectory(initialdir=os.getcwd(), title="Select graphs' directory")
        if csv2Plot(path=direct.replace('/','\\'), extension='emgdat') is False:
            self.setErrorMsg("ERROR: Files could not be open")
        else:
            self.setInfoMsg("Graphs shown")

    # selección de carpeta de salida de ficheros
    def selectOutputFolder(self):
        """ 
        @def    Abre ventana para seleccionar carpeta
        @arg    none
        @return none
        """
        # print("Output Folder")  # @note traza
        self.Folder.set(filedialog.askdirectory(initialdir=os.getcwd(), title="Select directory"))

    # inserta un mensaje de error
    def setErrorMsg(self, text):
        """ 
        @def    Muestra mensaje de error
        @arg    text texto a mostrar
        @return none
        """
        self.labMsg['text'] = text
        self.labMsg['foreground'] = "red"

    # inserta un mensaje de información
    def setInfoMsg(self, text):
        """ 
        @def    Muestra mensaje informativo
        @arg    text texto a mostrar
        @return none
        """
        self.labMsg['text'] = text
        self.labMsg['foreground'] = "black"
    
    # inserta un mesaje de precaución
    def setWarningMsg(self, text):
        """ 
        @def    Muestra mensaje de precaución
        @arg    text texto a mostrar
        @return none
        """
        self.labMsg['text'] = text
        self.labMsg['foreground'] = "orange"

# main
def main():
    """ 
    @def    Función principal del módulo
    @arg    none
    @return 0
    """
    root = tk.Tk()
    root.title("EMG Data Logger")
    root.minsize(175,75)
    root.resizable(width=False,height=False)
    main = MainWindow(root) 
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()

    return 0

if __name__ == '__main__':
    main()
    