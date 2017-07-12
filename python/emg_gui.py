from tkinter import *
from tkinter import ttk, font
from serial.tools import list_ports

# Gestor de geometría (pack)

class Aplicacion():
    def __init__(self):
        self.raiz = Tk()
        self.raiz.title("EMG Data Logger")
        
        # Cambia el formato de la fuente actual a negrita para
        # resaltar las dos etiquetas que acompañan a las cajas
        # de entrada. (Para este cambio se ha importado el  
        # módulo 'font' al comienzo del programa):
        
        fuente = font.Font(weight='bold')
        
        # Define los difrentes frames
        self.topFrame = ttk.Frame(self.raiz)
        self.bottomFrame = ttk.Frame(self.raiz)

        # define las etiquetas
        self.labPorts = ttk.Label(self.topFrame, text="COM:",
                                  font=fuente)


        # definición de Combobox
        self.portsList = StringVar()
        self.cbPort = ttk.Combobox(self.topFrame, textvariable=self.portsList)
        # eventos del combobox
        self.cbPort.bind('<<ComboboxSelected>>', self.imprimir)

        # definir separador
        self.separ1 = ttk.Separator(self.topFrame, orient=HORIZONTAL)
        
        # Se definen dos botones con dos métodos: El botón
        # 'Aceptar' llamará al método 'self.aceptar' cuando
        # sea presionado para validar la contraseña; y el botón
        # 'Cancelar' finalizará la aplicación si se llega a
        # presionar:
        self.boton1 = ttk.Button(self.bottomFrame, text="Aceptar", 
                                 command=self.aceptar)
        self.boton2 = ttk.Button(self.bottomFrame, text="Cancelar", 
                                 command=quit)
        self.bRefresh = ttk.Button(self.topFrame, text="Refresh", 
                                 command=self.actualizarPuertos)
                                 
        # Se definen las posiciones de los widgets dentro de
        # la ventana. Todos los controles se van colocando 
        # hacia el lado de arriba, excepto, los dos últimos, 
        # los botones, que se situarán debajo del último 'TOP':
        # el primer botón hacia el lado de la izquierda y el
        # segundo a su derecha.
        # Los valores posibles para la opción 'side' son: 
        # TOP (arriba), BOTTOM (abajo), LEFT (izquierda)
        # y RIGHT (derecha). Si se omite, el valor será TOP
        # La opción 'fill' se utiliza para indicar al gestor
        # cómo expandir/reducir el widget si la ventana cambia
        # de tamaño. Tiene tres posibles valores: BOTH
        # (Horizontal y Verticalmente), X (Horizontalmente) e 
        # Y (Verticalmente). Funcionará si el valor de la opción
        # 'expand' es True.
        # Por último, las opciones 'padx' y 'pady' se utilizan
        # para añadir espacio extra externo horizontal y/o 
        # vertical a los widgets para separarlos entre sí y de 
        # los bordes de la ventana. Hay otras equivalentes que
        # añaden espacio extra interno: 'ipàdx' y 'ipady':
        self.topFrame.pack()
        self.bottomFrame.pack(side=BOTTOM)

        self.labPorts.pack(side=LEFT, fill=BOTH, expand=True,
                          padx=5, pady=5)
        self.cbPort.pack(side=LEFT, fill=BOTH, expand=True,
                        padx=5, pady=5)
        self.bRefresh.pack(side=RIGHT, fill=BOTH, expand=True,
                        padx=5, pady=5)
        self.separ1.pack(side=TOP, fill=BOTH, expand=True, 
                         padx=5, pady=5)
        self.boton1.pack(side=LEFT, fill=BOTH, expand=True, 
                         padx=5, pady=5)
        self.boton2.pack(side=RIGHT, fill=BOTH, expand=True, 
                         padx=5, pady=5)

        # actualizar puertos (combobox)
        self.actualizarPuertos()

        
        # Cuando se inicia el programa se asigna el foco
        # a la caja de entrada de la contraseña para que se
        # pueda empezar a escribir directamente:
        
        self.raiz.mainloop()
    
    # El método 'aceptar' se emplea para validar la 
    # contraseña introducida. Será llamado cuando se 
    # presione el botón 'Aceptar'. Si la contraseña
    # coincide con la cadena 'tkinter' se imprimirá
    # el mensaje 'Acceso permitido' y los valores 
    # aceptados. En caso contrario, se mostrará el
    # mensaje 'Acceso denegado' y el foco volverá al
    # mismo lugar.
    
    def aceptar(self):
        print(self.cbPort.get())

    def imprimir(self, event):
        print("Seleccion:" + self.cbPort.get())

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

def main():
    mi_app = Aplicacion()
    return 0

if __name__ == '__main__':
    main()