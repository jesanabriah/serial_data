/*    
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

    Instrucciones:
    
    Conecte la entrada al pin A0 del conversor analogo digital.
    
    La salida es serial por el puerto USB y es de la forma: "time   temperature"
    
    Es decir, tiempo(segundos) y temperatura(100mV/℃). 
    
    No olvidar polarizar el sensor de temperatura a 5V para evitar dañar 
    el ADC son voltajes mayores a grandes temperaturas. (De existir ese riesgo)
*/

double temperature;

void setup(){
  //Inicializando la comunicacion serial
  Serial.begin(9600);
  //1.1V Para mayor precisión en el ADC, dado que nunca pasaremos de los 110 ℃
  analogReference(INTERNAL1V1);//1.1V (Arduino Mega only)
}

void loop(){
  //Serial print time in milliseconds
  Serial.print(millis()/1000.0, 3);
  //Serial print separator data "\t"
  Serial.print("\t");
  //Calculate and serial print temperature
  temperature = analogRead(A0)*0.010752688172;//1.1/1023*10
  //Dos cifras decimales, 
  //pues la precision del lm35 se toma como +- 0.5 ℃ 
  //para el rango de medición utilizado
  Serial.println(temperature, 2);
}
