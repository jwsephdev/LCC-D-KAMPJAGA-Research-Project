#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

int RXPin = 2;
int TXPin = 3;
int light = 8;
char t;
TinyGPSPlus gps;

SoftwareSerial gpsSerial(RXPin, TXPin);

void setup() {
  Serial.begin(9600);
  pinMode(light, OUTPUT);
  digitalWrite(light, HIGH);
  gpsSerial.begin(9600);
}

void loop() {
  while (gpsSerial.available() > 0)
    if (gps.encode(gpsSerial.read()))
      displayInfo();

  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println("No GPS detected");
    while (true)
      ;
  }

  if(Serial.available()){
  t = Serial.read();
  Serial.println(t);
}

if(t == 'U'){
  digitalWrite(light,LOW);
}
 
else if(t == 'u'){
  digitalWrite(light,HIGH);
}
}

void displayInfo() {
  if (gps.location.isValid()) {
    Serial.print("Latitude: ");
    Serial.println(gps.location.lat(), 6);
    Serial.print("Longitude: ");
    Serial.println(gps.location.lng(), 6);
    Serial.print("Altitude: ");
    Serial.println(gps.altitude.meters());
  } else {
    Serial.println("Location: Not Available");
  }

  Serial.print("Date: ");
  if (gps.date.isValid()) {
    Serial.print(gps.date.month());
    Serial.print("/");
    Serial.print(gps.date.day());
    Serial.print("/");
    Serial.println(gps.date.year());
  } else {
    Serial.println("Not Available");
  }

  Serial.print("Time: ");
  if (gps.time.isValid()) {
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour()+8);
    Serial.print(":");
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute());
    Serial.print(":");
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.print(gps.time.second());
//    Serial.print(".");
//    if (gps.time.centisecond() < 10) Serial.print(F("0"));
//    Serial.println(gps.time.centisecond());
  } else {
    Serial.println("Not Available");
  }

  Serial.println();
  Serial.println();
  delay(1000);
}