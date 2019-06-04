double temperature=0;
double entrada=0;

const int PWM_PIN = 13;
unsigned long t = 0;

//f(t) = sin(w * t) + 1.0
float w = 1.0; // rad/s
float sin_wt = 0.0;
float f_t = 1.0;

int value = 0;
int value_temp = 0;

//int delta = 0;

void setup(){
    Serial.begin(115200);
    pinMode(PWM_PIN, OUTPUT);
    
    //delta = (int)(0.0479368996/w);//2pi/1.024/32
    //1.1V Para mayor precisión en el ADC, dado que nunca pasaremos de los 110 ℃
    //analogReference(INTERNAL1V1);//1.1V (Arduino Mega only)
}

void loop()
{ 
    t = millis(); 
    sin_wt = sin(w/1000.0 * t);
    f_t = sin_wt*0.5 + 2.9;
    value = (int)(f_t*50.0);
    if (value != value_temp)
    {
        analogWrite(PWM_PIN, value);//f(t)*255/5
        value_temp = value;
    }    

    //Calculate and serial print temperature
    temperature = analogRead(A0)*0.048875855;//5/1023*10
    entrada = analogRead(A1)*0.004887586;//5/1023

    Serial.print(millis()/1000.0, 3);
    Serial.print("\t");
    Serial.print(temperature, 2);
    Serial.print("\t");
    Serial.println(entrada, 2);
    
    //delay(delta);
}
