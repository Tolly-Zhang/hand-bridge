#ifndef COMMON_H
#define COMMON_H

#include <Arduino.h>
#include <ESP32Servo.h>

class BluetoothSerial {
public:
    BluetoothSerial(char* name, char* pin = "1234");
    void establish_connection(Stream& s);
    bool available();
    String readStringUntil(char delimiter = '\n');
private:
    Stream* stream;
    char* device_name;
    char* pin_code;
};

class LED {
public:
    LED(uint8_t pin);
    void on();
    void off();
    void toggle();
private:
    uint8_t pin;
    bool state = false;
};

class Motor {
public:
    Motor(uint8_t pin, int min_pw, int max_pw);
    void setThrottle(int throttle);
private:
    Servo esc;
    uint8_t pin;
    int min_pw;
    int max_pw;
};

#endif // COMMON_H