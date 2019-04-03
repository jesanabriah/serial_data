#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    Copyright 2018 Jorge Sanabria
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.   
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import threading
import serial.tools.list_ports

#Historial de volumen
h_v = []

#Historial de presión
h_p = []

#Temperatura y numero de vueltas
t, n = 0, 0

#Variables temporales
temp_p, temp_v, temp_t, temp_n = [], [], 0, 0

#M es la cantidad de muestras visibles en el plot y por tanto el tamaño de los arreglos
M = 50

#Un numero bastante grande para que la animacion nunca termine
N = 100000

#Lee los puertos seriales habilitados en el sistema
comlist = serial.tools.list_ports.comports()
connected = []

#Revisa los puertos seriales conectados
for element in comlist:
    connected.append(element.device)

#Inicializa la comunicacion serial por el primer puerto habilitado
arduino = serial.Serial(connected[0], 115200, timeout=0.005)

#Esta funcion se ejecuta solo cuando inicia la animacion
def init():
    global h_p, h_v, t, n, temp_p, temp_v, temp_t, temp_n
    
    #inicializa los arreglos con ceros
    h_v = [0] * M
    h_p = [0] * M
    t = 0
    n = 0
    temp_p = [0] * M
    temp_v = [0] * M
    temp_t = 0
    temp_n = 0
    
    #Inicializa el plot
    line.set_data(h_v, h_p)
    return line,

#Esta funcion se repite continuamente
def animate(index, val,  line):
    global h_p, h_v, t, n, temp_p, temp_v, temp_t, temp_n
    
    #Asigna los valores temporales leidos serialmente desde el usb, en el plot
    h_p, h_v, t, n = temp_p, temp_v, temp_t, temp_n
    
    #Muestra la temperatura y grafica los datos
    plt.title("T = " + str(t) + r"$^\circ C$ :: N = " + str(n))                
    line.set_data([h_v, h_p])
    return line,

#Lee continuamente los datos desde el puerto serial USB
def read_data():
    global temp_p, temp_v, temp_t, temp_n
    while True:
        data = arduino.readline()[:-2]#Omite el fin de linea
        if data:
            try:
                #Lee cada dato del serial independientemente
                sp, sv, st, sn = data.split(":")
                if sp and sv and st:
                    #Agrega un nuevo elemento al top del array
                    temp_p.append(float(sp))
                    temp_v.append(float(sv) / 1023.0 * 45.2)#Ajuste en cm^3
                    #Borra el primer elemento del array, en cada caso
                    temp_p.pop(0)
                    temp_v.pop(0)
                    temp_t = float(st)
                    temp_n = int(sn)
            except ValueError:
                pass

# Crea un hilo de ejecucion exclusivo para la lectura de los datos seriales
t_read_data = threading.Thread(target=read_data)
t_read_data.start()

# Plot animacion
fig = plt.figure()
line,  = plt.plot([], [], '-')
plt.suptitle(u"Diagrama PV de maquina térmica")
plt.grid()

#Modificar estos valores de acuerdo a las necesidades del plot
#45.2 cm^3 es el mayor valor leido posible por el desplazamiento maximo del sensor
plt.xlim(0, 45.2)
#El sensor BMP180 tiene un rango de medicion para la presion entre 300 y 1100 hPa, segun el fabricante
plt.ylim(300, 1100)
plt.xlabel(r"$V\, / \,[cm^3]$")
plt.ylabel(r"$P\, / \,[hPa]$")

# Creando animaciones
# La funcion init se ejecuta solo al inicio de la animacion
# La funcion animate se ejecuta en cada iteracion
# La animacion se ejecuta N + 1 veces con el orden de indices dado por range(N + 1), como 0, 1, 2, 3, 4... N
# interval define el intervalo de tiempo entra cada animacion en milisegundos
# la opcion blit permite optimizar la animcacion, pero no sirve en todos los casos
# range(N + 1) y fargs, representan los argumentos obligatorios para la funcion animate
# retornando en "anim" es posible guardar la animacion posteriormente
anim = animation.FuncAnimation(fig, animate, range(N + 1),  fargs=(0,  line), interval = 100,  init_func=init,  repeat = False,  blit=False)

# La siguiente linea puede no comentarla para guardar un video con el registro de las medidas respectivas.
# Puede llegar a ser bastante lento dependiendo del tiempo de ejecución y de la velocidad de procesamiento 
# del computador utilizado.
#anim.save('stirling.mp4', fps=100, extra_args=['-vcodec', 'libx264'])

plt.show()
