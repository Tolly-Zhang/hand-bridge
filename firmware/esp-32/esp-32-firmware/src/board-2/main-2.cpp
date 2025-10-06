#include <Arduino.h>
#include <ESP32Servo.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

const uint8_t SERVO_PIN = 23;
const int MIN_PW = 500;      // Minimum pulse width in microseconds
const int MAX_PW = 2500;     // Maximum pulse width in microseconds
const int NEUTRAL_PW = 1500; // Neutral pulse width in microseconds

const int ROTATE_PW = 500;   // Pulse width for rotation

bool lightState = false;     // Current state of the light

Servo servo;                    // Create a Servo object

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

void rotate(bool direction) {
  // Move away from neutral in opposite directions for ON / OFF.
  int target = NEUTRAL_PW + (direction ? ROTATE_PW : -ROTATE_PW);
  target = constrain(target, MIN_PW, MAX_PW); // Clamp to valid range
  servo.writeMicroseconds(target);
  delay(800); // Hold position for a short time
  servo.writeMicroseconds(NEUTRAL_PW);                              // Return to neutral position
  lightState = direction;                                           // Update light state
}

void setup() {

  servo.setPeriodHertz(50);                  // Set frequency to 50 Hz
  servo.attach(SERVO_PIN, MIN_PW, MAX_PW);   // Attach the Servo
  servo.writeMicroseconds(1500);             // Initialize to mid-point (neutral position)
  
  Serial.begin(115200);
  SerialBT.begin("ESP32-BT");           // Name of your Bluetooth device
  SerialBT.setPin("1234");              // Set Bluetooth PIN (optional)
  establishSerialConnection(SerialBT);

}

void loop() {

  if (io->available()) {
    String command = io->readStringUntil('\n');
    command.trim();

    if (command == "LIGHT ON") {
      rotate(true);
      io->println("LIGHT is ON");
    } 
    else if (command == "LIGHT OFF") {
      rotate(false);
      io->println("LIGHT is OFF");
    } 
    else if (command == "LIGHT TOGGLE") {
      rotate(!lightState);
      io->println(String("LIGHT is ") + (lightState ? "ON" : "OFF"));
    }
    else {
      io->println("Unknown command. Use 'LIGHT ON', 'LIGHT OFF', or 'LIGHT TOGGLE'.");
    } 
  }

}