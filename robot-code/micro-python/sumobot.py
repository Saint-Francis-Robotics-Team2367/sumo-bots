import socket
import network
import time
from machine import Pin, PWM, ADC
import threading

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
        print('Receiving on UDP Port...')
        while True:
            print(self.read_udp_packet())
            time.sleep(1)

    ### Called by user to receive the data from UDP
    ### The output either will show the updated game state or the controller status depending on game state
    def broadcast(self, debug=""):
        try:
            name = "!" + self.robot_name + "@" + debug
            while True:
                self.socket.sendto(name.encode(), ("255.255.255.255", 2367))
                time.sleep(1)
        except:
            os._exit(1)

    def read_udp_packet(self):
        data = None
        try:
            data, addr = self.socket.recvfrom(1024)
        except:
            return {"data": None}

        if len(data) == 24:
            return self.parse_robot_command(data)
        elif len(data) == 65:
            return self.parse_game_state(data)
        else:
            return (data, "from ", addr)


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


bot = SumoBot("Hi")
