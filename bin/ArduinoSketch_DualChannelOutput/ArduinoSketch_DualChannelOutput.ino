/*
This sketch generates data array from Arduino Uno board on request.
A analog input pin reads voltage output from Dual-Channel powermeter.

Author: jkkow
Last updated: 2017-10-30T09:00:53
*/

int Ch1 = A0;
int Ch2 = A1;

void setup(){
  // Set analog read pins to read output voltage from two channel of Dual-Channel powermeter
  pinMode(Ch1, INPUT);
  pinMode(Ch2, INPUT);
  // Open serial port
  Serial.begin(9600);
}

void loop(){
  if(Serial.available())
  {
    if(Serial.find('r'))
       {
        int ch1_out = analogRead(Ch1);
        int ch2_out = analogRead(Ch2);
        Serial.println(ch1_out);
        Serial.println(ch2_out);
        }
  }
}

