#include <Arduino.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

const uint8_t LED_PIN = 23;

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

void setup() {

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.begin(115200);
  SerialBT.begin("ESP32-BT"); // Name of your Bluetooth device
  establishSerialConnection(SerialBT);

}

void loop() {

  if (io->available()) {
    String command = io->readStringUntil('\n');
    command.trim();

    if (command == "LED ON") {
      digitalWrite(LED_PIN, HIGH);
      io->println("LED is ON");
    } else if (command == "LED OFF") {
      digitalWrite(LED_PIN, LOW);
      io->println("LED is OFF");
    } else {
      io->println("Unknown command. Use 'LED ON' or 'LED OFF'.");
    }
  }

}