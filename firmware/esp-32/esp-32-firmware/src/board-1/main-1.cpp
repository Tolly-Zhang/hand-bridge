#include <Arduino.h>
#include <ESP32Servo.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

const uint8_t LED_PINS[4] = {23, 22, 19, 18};

const uint8_t ESC_PIN = 17;

const int FULL_MIN_PW = 500;
const int FULL_MAX_PW = 2500;
const int USED_MIN_PW = 1110;
const int USED_MAX_PW = 1900;

const int ARM_PW = 900;         // Pulse width to arm the ESC

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
  int pulseWidth = map(throttle, 0, 100, USED_MIN_PW, USED_MAX_PW);
  esc.writeMicroseconds(pulseWidth);
}

void setup() {

  for (uint8_t i = 0; i < sizeof(LED_PINS); i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }

  esc.setPeriodHertz(50);               // Set frequency to 50 Hz
  esc.attach(ESC_PIN, FULL_MIN_PW, FULL_MAX_PW);  // Attach the ESC
  esc.writeMicroseconds(ARM_PW);           // Initialize throttle to 0%
  delay(3000);                          // Wait for 3 seconds to allow ESC to initialize
  setThrottle(0);                      // Ensure throttle is at 0%
  
  Serial.begin(115200);
  SerialBT.begin("ESP32-BT");           // Name of your Bluetooth device
  SerialBT.setPin("1234");              // Set Bluetooth PIN (optional)
  establishSerialConnection(SerialBT);

}

void loop() {

  if (io->available()) {
    String command = io->readStringUntil('\n');
    command.trim();

    if (command.startsWith("LED ")) {
      String ledCmd = command.substring(4); // Get the part after 'LED '

      char state = ledCmd.charAt(0);

      if ((state == 'H' || state == 'L' || state == 'T') && ledCmd.length() > 2 && ledCmd.charAt(1) == ' ') {
        int ledIndex = ledCmd.substring(2).toInt();

        if (ledIndex >= 0 && ledIndex < sizeof(LED_PINS)) {

          if (state == 'T') {
            // Toggle the LED state
            int currentState = digitalRead(LED_PINS[ledIndex]);
            digitalWrite(LED_PINS[ledIndex], currentState == HIGH ? LOW : HIGH);
            io->println("LED" + String(ledIndex) + " toggled to " + (currentState == HIGH ? "LOW" : "HIGH"));
          } 

          else {
            // Set the LED state to HIGH or LOW
            digitalWrite(LED_PINS[ledIndex], state == 'H' ? HIGH : LOW);
            io->println("LED" + String(ledIndex) + " is " + (state == 'H' ? "HIGH" : "LOW"));
          }

        } 
        
        else {
          io->println("Invalid LED index.");
        }

      } else {
        io->println("Unknown LED command. Use 'LED H <index>' or 'LED L <index>' or 'LED T <index>'.");
      }

    }
    else if (command.startsWith("THROTTLE ")) {
      int value = command.substring(9).toInt();

      setThrottle(value);
      io->println("Throttle set to " + String(value) + "%");

    }
    else {
      io->println("Unknown command. Use 'LED H <index>', 'LED L <index>', 'LED T <index>', or 'THROTTLE <value>'.");
    }
  }

}