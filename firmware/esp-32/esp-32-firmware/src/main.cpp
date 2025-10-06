#include <Arduino.h>

const uint8_t LED_PIN = 23;

void establishSerialConnection() {
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
  String message = Serial.readStringUntil('\n');
  message.trim();
  while (message != "READY") {
    message = Serial.readStringUntil('\n'); // wait for the "READY" message from the host
  }
  Serial.println("READY_ACK");
    
}

void setup() {

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  establishSerialConnection();

}

void loop() {
 
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED is ON");
    } else if (command == "OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED is OFF");
    } else {
      Serial.println("Unknown command. Use 'ON' or 'OFF'.");
    }
  }

}