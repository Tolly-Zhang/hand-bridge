import time
import serial.tools.list_ports as lp
import serial

DEFAULT_PORT = "COM3"
DEFAULT_BAUD = 115200

class ESP32SerialAdapter:

    def __init__(self, port: str = DEFAULT_PORT, baud: int = DEFAULT_BAUD) -> None:
        self.port = port
        self.baud = baud
        self.serial_connection = None
    
    def list_ports(self) -> None:
        ports = lp.comports()
        print("Available serial ports:")
        for port in ports:
            print(f"  Port: {port.device}")

    def set_port(self, port: str) -> None:
        self.port = port

    def open_serial(self) -> None:
        self.serial_connection = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2)  # Wait for the connection to establish
        print(f"Connected to {self.port} at {self.baud} baud.")

    def close_serial(self) -> None:
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.flush()
            self.serial_connection.close()
        print("Serial connection closed.")

    def establish_connection(self) -> None:
        pass

    def write_line(self, s: str) -> None:
        if not self.serial_connection.is_open:
            raise ConnectionError("Serial port is not open.")
            
        self.serial_connection.write((s + "\n").encode('utf-8'))
        print(f"Sent: {s}")

    def close(self) -> None:
        pass

serial_test = ESP32SerialAdapter()
serial_test.list_ports()
serial_test.open_serial()
while True:
    serial_test.write_line("ON")
    time.sleep(1)
    serial_test.write_line("OFF")
    time.sleep(1)