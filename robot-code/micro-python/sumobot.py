import socket
import time
from machine import Pin, PWM, ADC

class SumoBot:
    ### Sets up the ESP32 dev board and connects to the Wi-Fi network
    ### Does not return and is not user-facing
    def __init__(self, robot_name="default", ssid="WATCHTOWER", password="lancerrobotics", port=2367):
        self.robot_name = robot_name
        self.my_game_state = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
        print('network config:', wlan.ifconfig())
        print("Connected to Wi-Fi. IP:", wlan.ifconfig()[0])
        self.socket.bind(('', port))
        print('Receiving on UDP Port...')

    ### Called by user to receive the data from UDP
    ### The output either will show the updated game state or the controller status depending on game state
    def read_udp_packet(self):
        data = None
        while data is None:
            data, addr = self.socket.recvfrom(1024)
        if len(data) == 24:
            return self.parse_robot_command(data)
        elif len(data) == 65:
            return self.parse_game_state(data)


    ### Parses the UDP data to apply the game state to the robot if applicable
    ### Returns a message with the game state for user info, no action required with this information
    def parse_game_state(self, data):
        game_state = data.pop(0)
        hex_list = [hex(byte) for byte in data]
        # Get the robot names out in hexadecimal for comparison
        names_hex = [hex_list[i:i+16] for i in range(0, len(hex_list), 16)]
        # Find out if the game state command is applicable to this robot
        for elem in names_hex:
            name_called = bytes(int(hex_val, 16) for hex_val in hex_list)
            if name_called == self.robot_name:
                self.my_game_state = game_state >> 2
                return {"game_state": int(self.my_game_state)}
        return {"game_state": "N/A"}


    ### Parses the UDP data to get the controller inputs as is relevant to the robot
    ### Returns the controller input states as a dictionary
    def parse_robot_command(self, data):
        if self.my_game_state != 3:
            return -1
        name_hex = data[0:16]
        name_called = bytes(int(hex_val, 16) for hex_val in name_hex)
        if name_called != self.robot_name:
            return 0 
        controller_data = data[17:]
        controller_state = {
            "joystick_left_x": controller_data[0],
            "joystick_left_y": controller_data[1],
            "joystick_right_x": controller_data[2],
            "joystick_right_y": controller_data[3],
            "trigger_left": controller_data[4],
            "trigger_right": controller_data[5],
            "button_data": str(controller_data[6])+str(controller_data[7])
        }
        return controller_state



class Motor:
    ### Sets up motor controller for user control
    ### Does not return
    def __init__(self, pin1, pin2, speed_limit=0.5, pwm_freq=2000):
        assert speed_limit<=1 and speed_limit>0
        self.pin1 = PWM(Pin(pin1), pwm_freq)
        self.pin2 = PWM(Pin(pin2), pwm_freq)
        self.speed_limit = speed_limit

    ### Gives user control of driving the robot while abstracting PWM signals from them
    ### Does not return
    def drive(self, speed):
        assert speed<=1 and speed>=-1
        duty_cycle = round(self.speed_limit*abs(speed)*1023)
        if speed<0:
            self.pin1.duty(duty_cycle)
            self.pin2.duty(0)
        elif speed>0:
            self.pin1.duty(0)
            self.pin2.duty(duty_cycle)
        else:
            self.pin1.duty(0)
            self.pin2.duty(0)
            
class Sensor:
    def __init__(self, pin, signal_type, converter_pin):
        self.pin_id = pin
        if (signal_type=="digital"):
            val = read_digital(converter_pin)
        elif (signal_type=="analog"):
            val = read_analog(converter_pin)
        return val
            
    def read_analog(pin):
        adc = ADC(Pin(pin))
        val = adc.read_u16()
        val = adc.read_uv()
        return val
    
    def read_digital(pin):
        adc = ADC(Pin(pin))
        val = adc.read_u16()
        val = adc.read_uv()
        return val


# Function to convert ADC value to distance
def adc_to_distance(adc_value):
    volts = adc_value*0.0048828125
    distance = 40*pow(volts, -1)
    return distance

    # Main loop to continuously read the distance
    while True:
        adc_value = adc.read()  # Read the ADC value from GPIO32
        distance = adc_to_distance(adc_value)  # Convert ADC value to distance
        print("Distance: " + distance)  # Print the distance value
        time.sleep(0.1)  # Delay for half a second before the next reading"""

    input_pin = Pin(33, Pin.IN)
    while True:
            value = input_pin.value()  # Read the digital value (0 or 1)
            print("GPIO 33 value:", value)  # Print the value to the console
            time.sleep(0.1)  # Wait

def main():
    # Initialize a distance sensor
    distance_sensor = Sensor(pin=32, signal_type="analog", converter_pin=10) # changed pin number
    while(true):
        distance = adc_to_distance()
        print("Distance: " + distance)
        time.sleep(1)