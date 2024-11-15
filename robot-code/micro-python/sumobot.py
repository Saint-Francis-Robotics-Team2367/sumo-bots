import socket
import network
import time
from machine import Pin, PWM, ADC
import _thread

## Unclaimed = 0
## Standby = 1
## Autonomy = 2
## Teleoperation = 3


class SumoBot:
    ### Sets up the ESP32 dev board and connects to the Wi-Fi network
    ### Does not return and is not user-facing
    def __init__(self, robot_name="default", ssid="WATCHTOWER", password="lancerrobotics", port=2367):
        self.robot_name = robot_name
        led = Pin(2, Pin.OUT) # LED declaration
        self.game_state = 0 # game state of the robot
        self.leftSpeed = 0 # left value of the joystick 
        self.rightSpeed = 0 # right value of the joystick
        self.controller_state = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
            
        print('network config:', wlan.ifconfig())
        print("Connected to Wi-Fi. IP: ", wlan.ifconfig()[0])
        led.value(1) # LED on when Wi-Fi connected
        

        self.socket.bind(('', port))
        print('Receiving on UDP Port...')

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
            controller_state = self.parse_robot_command(data) # get controller state
            if controller_state != -1 and controller_state != 0: 
                self.leftSpeed = controller_state["joystick_left_y"] # get left joystick y value
                self.rightSpeed = controller_state["joystick_right_y"] # get right joystick y value
        else:
            self.game_state = self.parse_game_state(data) # get game state of robot currently
        
            
    
    ### Parses the UDP data to apply the game state to the robot if applicable
    ### Returns a message with the game state for user info, no action required with this information
    def parse_game_state(self, data):
        data = data.decode('utf-8')
        if data == "Standby":
            self.game_state = 1
            self.controller_state = {}
        if data == "Autonomy":
            self.game_state = 2
            self.controller_state = {}
        elif data == "Teleoperation":
            self.game_state = 3
        else:
            return 0
        return self.game_state


    ### Parses the UDP data to get the controller inputs as is relevant to the robot
    ### Returns the controller input states as a dictionary
    def parse_robot_command(self, data):
        if self.game_state != 3:
            return -1
        name_hex = data[0:16]
        name_called = name_hex.decode('utf-8').rstrip('\x00')
        if name_called != self.robot_name:
            return 0 
        controller_data = data[16:]
        controller_state = {
            "joystick_left_x": controller_data[0],
            "joystick_left_y": controller_data[1],
            "joystick_right_x": controller_data[2],
            "joystick_right_y": controller_data[3],
            "trigger_left": controller_data[4],
            "trigger_right": controller_data[5]
        }
        
        self.controller_state = controller_state
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
    def __init__(self, pin_number):
        self.pin_num = pin_number
        self.pin = None

    ### Reads analog signals coming from the sensor
    ### Returns analog value
    def read_analog(self):
        if type(self.pin) != ADC:
            self.pin = ADC(Pin(self.pin_num))
        return self.pin.read()
    
    ### Reads digital signals coming from the sensor
    ### Returns digital value
    def read_digital(self):
        if type(self.pin) != Pin:
            self.pin = Pin(self.pin_num, Pin.IN, Pin.PULL_DOWN)
        return self.pin.value()

bot = SumoBot("TEAM_NAME_HERE") # bot declarations

leftmotor = Motor(18, 19)
rightmotor = Motor(21, 22)

leftmotor.drive(0)
rightmotor.drive(0)

# Run this code for Team 1
while True:
    # get the game state and controller values
    bot.read_udp_packet()
    
    if(bot.game_state == 0): # if it is in standby mode, do nothing
        leftmotor.drive(0)
        rightmotor.drive(0)
    elif(bot.game_state == 2): # if it is in auto, do auto-code
        # put team auto code here
        leftmotor.drive(0)
        rightmotor.drive(0)
    elif(bot.game_state == 3): # if it is in tele-op, start moving motors
        lefty = (int(bot.leftSpeed) - 128)/128
        righty = (int(bot.rightSpeed) - 128)/128
        print(lefty, bot.leftSpeed)
        print(righty, bot.rightSpeed)
        leftmotor.drive(-1*lefty)
        rightmotor.drive(righty)

