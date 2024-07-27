import socket
import network
import time

ROBOT_NAME = "St. Francis"
SSID = "WATCHTOWER"
PASSWORD = "lancerrobotics"
PORT = 2367
my_game_state = 0


### Called by user to receive the data from UDP
### The output either will show the updated game state or the controller status depending on game state
def read_udp_packet(data):
	data = None
	while data == None:
		data, addr = s.recvfrom(1024)

	if len(data) == 24:
		return parse_robot_command(data)

	elif len(data) == 65:
		return parse_game_state(data)


### Parses the UDP data to apply the game state to the robot if applicable
### Returns a message with the game state for user info, no action required with this information
def parse_game_state(data):
	hex_list = [hex(byte) for byte in data]
	game_state = data.pop(0)

	#find out if the game state command is applicable to this robot
	for elem in [hex_list[i:i+16] for i in range(0, len(hex_list), 16)]:
		name_called = bytes(int(hex_val, 16) for hex_val in hex_list)
		if name_called == ROBOT_NAME:
			my_game_state = game_state >> 2
			return "Game State Update: " + my_game_state
	return "Game State Update: N/A"


### Parses the UDP data to get the controller inputs as is relevant to the robot
### Returns the controller input states as a dictionary
def parse_robot_command(data):
	if game_state != 3:
		return -1
	name_hex = data[0:16]
	name_called = bytes(int(hex_val, 16) for hex_val in name_hex)
	if name_called != ROBOT_NAME:
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

### Sets up the ESP32 dev board to connect to the Wi-Fi network
### Does not return and is not user-facing
def connect_to_wifi():
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.connect(SSID, PASSWORD)
	
	while not wlan.isconnected():
		print("Connecting to Wi-Fi...")
		time.sleep(1)
	
	print("Connected to Wi-Fi. IP:", wlan.ifconfig()[0])
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', PORT)) #binding the port
	print('Receiving on UDP Port...')
