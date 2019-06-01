#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    Copyright 2019 Jorge Sanabria
    
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
from matplotlib.widgets import Slider

# Valores minimo, maximo y por defecto para el slider
MINVAL, MAXVAL, VAL0 = 0.0, 60.0, 5.0

# Valores maximo, minimo y muestreo para el plot en el eje x
# No arrancar en cero para evitar overflow
XMIN_RANGE, XMAX_RANGE = 0.0, 300.0
YMIN_RANGE, YMAX_RANGE = 0.0, 15.0

#Historial de tiempo
h_time = []

#Historial de temperatura
h_temperature = []

#Variables temporales
temp_temperature, temp_time = 0, 0

#Un numero bastante grande para que la animacion nunca termine
N = 100000

#Lee los puertos seriales habilitados en el sistema
comlist = serial.tools.list_ports.comports()
connected = []

#Revisa los puertos seriales conectados
for element in comlist:
    connected.append(element.device)
    print element.device

#Inicializa la comunicacion serial por el puerto seleccionado
arduino = serial.Serial(connected[1], 115200)#, timeout=0)

#Esta funcion se ejecuta solo cuando inicia la animacion
def init():
    global h_temperature, h_time, temp_temperature, temp_time
    
    h_time = [0]
    h_temperature = [0]
    temp_temperature = 0
    temp_time = 0

    #Inicializa el plot
    line.set_data(h_time, h_temperature)
    return line,

#Esta funcion se repite continuamente
def animate(index, val,  line):
    global h_temperature, h_time, temp_temperature, temp_time
    
    #Asigna los valores temporales leidos serialmente desde el usb, en el plot    
    h_temperature.append(temp_temperature)
    h_time.append(temp_time)
    
    #grafica los datos              
    line.set_data([h_time, h_temperature])
    
    return line,

#Lee continuamente los datos desde el puerto serial USB
def read_data():
    global temp_temperature, temp_time
    while True:
        data = arduino.readline()[:-2]#Omite el fin de linea 
        if data:
            try:
                #Lee cada dato del serial independientemente
                stime, stemperature = data.split("\t")
                if stemperature and stime:
                    #Agrega un nuevo elemento al top del array
                    temp_temperature = float(stemperature)
                    temp_time = float(stime)#Ajuste en cm^3
                    print temp_time, "\t", temp_temperature
            except ValueError:
                pass

# Plot animacion
fig = plt.figure()
plt.suptitle(u"Diagrama T vs t de planta térmica")
plt.grid()
ax = fig.add_subplot(111)
line,  = ax.plot([], [])#, '.')
# Adjust the subplots region to leave some space for the sliders and buttons
fig.subplots_adjust(bottom=0.25)
ax.set_xlim([XMIN_RANGE, XMAX_RANGE])
ax.set_ylim([YMIN_RANGE, YMAX_RANGE])

#plt.axis("scaled")
ax.set_xlabel(r"$t\, / \,[s]$")
ax.set_ylabel(r"$T\, / \,[V]$")

# Define an axes area and draw a slider in it
amp_slider_ax  = fig.add_axes([0.15, 0.05, 0.7, 0.05])
amp_slider = Slider(amp_slider_ax, 'X Adjust', MINVAL, MAXVAL, valinit=VAL0)

# Define an action for modifying the line when any slider's value changes
def sliders_on_changed(val):
    ax.set_xlim([XMIN_RANGE, XMAX_RANGE * amp_slider.val])
    ax.set_ylim([YMIN_RANGE, YMAX_RANGE])
    fig.canvas.draw_idle()
    
amp_slider.on_changed(sliders_on_changed)

# Crea un hilo de ejecucion exclusivo para la lectura de los datos seriales
t_read_data = threading.Thread(target=read_data)
t_read_data.start()

# Creando animaciones
# La funcion init se ejecuta solo al inicio de la animacion
# La funcion animate se ejecuta en cada iteracion
# La animacion se ejecuta N + 1 veces con el orden de indices dado por range(N + 1), como 0, 1, 2, 3, 4... N
# interval define el intervalo de tiempo entra cada animacion en milisegundos
# la opcion blit permite optimizar la animcacion, pero no sirve en todos los casos
# range(N + 1) y fargs, representan los argumentos obligatorios para la funcion animate
# retornando en "anim" es posible guardar la animacion posteriormente
anim = animation.FuncAnimation(fig, animate, range(N + 1),  fargs=(0,  line), interval = 1,  init_func=init,  repeat = True,  blit=True)

# La siguiente linea puede no comentarla para guardar un video con el registro de las medidas respectivas.
# Puede llegar a ser bastante lento dependiendo del tiempo de ejecución y de la velocidad de procesamiento 
# del computador utilizado.
#anim.save('plot.mp4', fps=100, extra_args=['-vcodec', 'libx264'])

plt.show()
