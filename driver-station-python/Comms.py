import socket
import pygame
import tkinter as tk
from threading import Thread
import time
import struct

# ESP32 IP addresses and ports 
# Make sure you change these values after each esp is connected to the wifi
ESP32_ADDRESSES = [
    ("192.168.0.101", 2367),
    ("192.168.0.102", 2367),
    ("192.168.0.103", 2367),
    ("192.168.0.104", 2367)
]

# UDP Setup
udp_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)] #setup 4 different sockets for each ESP32
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #setup a broadcast socket for all ESP32s gamestate
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Game state
game_status = get_game_status()  # could be "standby", "auto", "teleop"

# Initialize Pygame for controller input
pygame.init()
pygame.joystick.init()
controllers = [pygame.joystick.Joystick(i) for i in range(4)]
for controller in controllers:
    controller.init()

# Tkinter GUI
root = tk.Tk()
root.title("Driver Station")

status_var = tk.StringVar()
status_var.set("Status: Standby")

# Function to encode controller data
def encode_controller_data(controller):
    # Read the axis and button values
    axes = [controller.get_axis(i) for i in range(controller.get_numaxes())]
    buttons = [controller.get_button(i) for i in range(controller.get_numbuttons())]

    # Encode as bytes (example: use struct to pack the data)
    data = struct.pack(f'{len(axes)}f{len(buttons)}B', *axes, *buttons)
    return data

# Function to send controller data to ESP32
def send_controller_data():
    while True:
        pygame.event.pump()
        for i, controller in enumerate(controllers):
            data = encode_controller_data(controller)
            udp_sockets[i].sendto(data, ESP32_ADDRESSES[i])
        time.sleep(0.05)  # Send data at ~20Hz

# Function to send broadcast packets for game status
def broadcast_game_status():
    while True:
        packet = game_status.encode()
        broadcast_socket.sendto(packet, ("<broadcast>", 12345))
        time.sleep(1)  # Broadcast every second

# Tkinter callbacks for game status
def set_standby():
    global game_status
    game_status = "standby"
    status_var.set("Status: Standby")

def set_auto():
    global game_status
    game_status = "auto"
    status_var.set("Status: Autonomous")

def set_teleop():
    global game_status
    game_status = "teleop"
    status_var.set("Status: Teleop")

# GUI setup
tk.Label(root, text="Driver Station Control").pack()
tk.Label(root, textvariable=status_var).pack()

tk.Button(root, text="Standby", command=set_standby).pack()
tk.Button(root, text="Autonomous", command=set_auto).pack()
tk.Button(root, text="Teleop", command=set_teleop).pack()

# Start threads for sending data
Thread(target=send_controller_data, daemon=True).start()
Thread(target=broadcast_game_status, daemon=True).start()

# Start Tkinter main loop
root.mainloop()

# Clean up sockets on exit
for sock in udp_sockets:
    sock.close()
broadcast_socket.close()