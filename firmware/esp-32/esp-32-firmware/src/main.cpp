#include <Arduino.h>

const uint8_t LED_PIN = 23;

void setup() {

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);

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