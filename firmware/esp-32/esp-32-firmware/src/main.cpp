#include <Arduino.h>
const uint8_t LED_PIN = 23;
void setup() {

  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  Serial.println("Hello, ESP32!");
}

void loop() {
 
  Serial.println("LED ON");
  digitalWrite(LED_PIN, HIGH);
  delay(3000);
  digitalWrite(LED_PIN, LOW);
  Serial.println("LED OFF");
  delay(3000);

}