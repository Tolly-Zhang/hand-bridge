#include <Arduino.h>
#include <ESP32Servo.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

const uint8_t LED_PIN = 23;

const uint8_t ESC_PIN = 22;
const int MIN_PW = 1110;      // Minimum pulse width in microseconds
const int MAX_PW = 1900;      // Maximum pulse width in microseconds
Servo esc;                    // Create a Servo object to control the ESC

Stream* io = &SerialBT;

void establishSerialConnection(Stream& s) {

  s.setTimeout(2000); // Set a timeout for reading

  String message = s.readStringUntil('\n');
  message.trim();
  while (message != "READY") {
    message = s.readStringUntil('\n'); // wait for the "READY" message from the host
    message.trim();
  }
  s.println("READY_ACK");

}

void setThrottle(int throttle){
  throttle = constrain(throttle, 0, 100);
  int pulseWidth = map(throttle, 0, 100, MIN_PW, MAX_PW);
  esc.writeMicroseconds(pulseWidth);
}

void setup() {

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  esc.setPeriodHertz(50);               // Set frequency to 50 Hz
  esc.attach(ESC_PIN, MIN_PW, MAX_PW);  // Attach the ESC
  esc.writeMicroseconds(1000);        // Initialize throttle to 0%
  
  Serial.begin(115200);
  SerialBT.begin("ESP32-BT");           // Name of your Bluetooth device
  SerialBT.setPin("1234");              // Set Bluetooth PIN (optional)
  establishSerialConnection(SerialBT);

}

void loop() {

  if (io->available()) {
    String command = io->readStringUntil('\n');
    command.trim();

    if (command == "LED ON") {
      digitalWrite(LED_PIN, HIGH);
      io->println("LED is ON");
    } 
    else if (command == "LED OFF") {
      digitalWrite(LED_PIN, LOW);
      io->println("LED is OFF");
    } 
    else if (command.startsWith("THROTTLE ")) {
      int value = command.substring(9).toInt();
      setThrottle(value);
      io->println("Throttle set to " + String(value) + "%");
    }
    else {
      io->println("Unknown command. Use 'LED ON' or 'LED OFF'.");
    }
  }

}