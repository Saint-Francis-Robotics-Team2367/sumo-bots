import socket
import network
import time
from machine import Pin, PWM, ADC

## Unclaimed = 0
## Standby = 1
## Autonomy = 2
## Teleoperation = 3

class SumoBot:
    ### Sets up the ESP32 dev board and connects to the Wi-Fi network
    ### Does not return and is not user-facing
    def __init__(self, robot_name="default", ssid="WATCHTOWER", password="lancerrobotics", port=2367):
        self.robot_name = robot_name
        self.my_game_state = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
        print('network config:', wlan.ifconfig())
        print("Connected to Wi-Fi. IP: ", wlan.ifconfig()[0])
        self.socket.bind(('', port))
        connect_to_station()
        print('Receiving on UDP Port...')

    ### Called by user to receive the data from UDP
    ### The output either will show the updated game state or the controller status depending on game state
    def read_udp_packet(self):
        data = None
        name = "!" + self.robot_name + "@"
        self.socket.sendto(name.encode(), ("255.255.255.255", 2367))

        try:
            data, addr = self.socket.recvfrom(1024)
        except:
            return {"data": None}

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
    ### Sets up a sensor given pin number and sensor type
    ### Does not return
    def __init__(self, pin_number, pin_type):
        assert pin_type=="analog" or pin_type=="digital"
        self.pin_num = pin_number
        if pin_type=="analog":
            self.pin_type = "analog"
            self.reading = ADC(Pin(self.pin_num))
        else:
            self.pin_type = "digital"
            self.reading = Pin(self.pin_num, Pin.IN)

    ### Reads analog signals coming from the sensor
    ### Returns analog value
    def read_analog(self):
        assert(self.pin_type=="analog")
        val = self.reading.read()
        return val
    
    ### Reads digital signals coming from the sensor
    ### Returns digital value
    def read_digital(self):
        assert(self.pin_type=="digital")
        val = self.reading.value()
        return val
