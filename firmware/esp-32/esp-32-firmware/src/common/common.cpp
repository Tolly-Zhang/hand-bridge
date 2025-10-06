#include <common.h>

const int PW_MIN = 1000;

const int PW_LOW = 1110;
const int PW_HIGH = 1900;

BluetoothSerial::BluetoothSerial(char* name, char* pin) : device_name(name), pin_code(pin) {
    extern BluetoothSerial SerialBT;
    stream = &SerialBT;
    // UNFINISHED
}

LED::LED(uint8_t pin) : pin(pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
}

void LED::on() {
    digitalWrite(pin, HIGH);
    state = true;
}

void LED::off() {
    digitalWrite(pin, LOW);
    state = false;
}

void LED::toggle() {
    if (state) {
        off();
    } else {
        on();
    }
}

Motor::Motor(uint8_t pin, int min_pw, int max_pw) : pin(pin), min_pw(min_pw), max_pw(max_pw) {
    esc.setPeriodHertz(50);
    esc.attach(pin, min_pw, max_pw);
    esc.writeMicroseconds(PW_MIN);
}
    
void Motor::setThrottle(int throttle) {
    throttle = constrain(throttle, 0, 100);
    int pw = map(throttle, 0, 100, min_pw, max_pw);
    esc.writeMicroseconds(pw);
}   