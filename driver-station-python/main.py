import tkinter as tk
from tkinter import ttk
import socket
import pygame
import tkinter as tk
from threading import Thread
import time
import struct


#TODO:
# Find an esp to see if we can read properly
# Add readudp code to robot code as well as static ip addresses
# Nice to have: get comfirmations from ESP32 (not necessary)


# ESP32 IP addresses and ports 
# Make sure you change these values after each esp is connected to the wifi
# On game day we need to fill this out with every team and their esp32's ip address
robots = [
    {"name": "Team 1", "ip_address": ("192.168.0.101", 2367), "controller": None},
    {"name": "Team 2", "ip_address": ("192.168.0.102", 2367), "controller": None},
    {"name": "Team 3", "ip_address": ("192.168.0.103", 2367), "controller": None},
    {"name": "Team 4", "ip_address": ("192.168.0.104", 2367), "controller": None},
]

active_controllers = []

# To track the active button
active_button = None
button_order = ["Standby", "Autonomy", "Teleoperation"]

def get_game_state():
    return active_button["text"]

# Function to connect robots to controllers in UI
def connect_robot(robot_name, controller_name):
    #Creates a lit of all the robots and controllers with the same name as input (should be only 1)
    named_robots = [robot for robot in robots if robot["name"] == robot_name]
    named_controllers = [controller for controller in active_controllers if controller["name"] == controller_name]
    if len(named_robots) != 1 or len(named_controllers) != 1:
        print("Failed to connect (name mismatch)")
        return
    # Sets the robots "controller" to the controller object so we can now easily send all the controller values to that robot
    named_robots[0]["controller"] = named_controllers[0]["obj"]
    print(f"Connected {robot_name} to {controller_name}")

# Function to toggle button states
def toggle_button(new_active):
    global active_button
    # Deactivate the previously active button
    if active_button:
        active_button["relief"] = "raised"
        active_button["bg"] = "SystemButtonFace"  # Reset to default button color

    # Activate the new button
    active_button = new_active
    active_button["relief"] = "sunken"
    active_button["bg"] = "lightgreen"  # Set active button color

# Keyboard shortcut function to rotate buttons
def on_spacebar_press(event):
    global button_order
    current_idx = button_order.index(active_button["text"])
    next_idx = (current_idx + 1) % len(button_order)
    toggle_button(buttons[button_order[next_idx]])

# Function to send broadcast packets for game status
def broadcast_game_status():
    while True:
        game_state = get_game_state()
        packet = game_state.encode()
        broadcast_socket.sendto(packet, ("<broadcast>", 2367))
        time.sleep(1)  # Broadcast every second

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
        for i, controller in enumerate(active_controllers):
            # For all active controllers find every robot it is connected to and send data to each one
            robots_connected = [robot for robot in robots if robot["controller"] == controller["obj"]]
            data = encode_controller_data(controller["obj"])
            for bots in robots_connected:
                udp_sockets[i].sendto(data, bots["ip_address"])
        time.sleep(0.05)  # Send data at ~20Hz

def refresh_controllers():
    active_controllers.clear()
    # Detect all available joysticks
    num_joysticks = pygame.joystick.get_count()
    print(f"Number of joysticks detected: {num_joysticks}")

    for i in range(num_joysticks):
        joystick = pygame.joystick.Joystick(i)  # Initialize joystick
        joystick.init()
        
        # Get joystick details
        joystick_info = {
            "id": i,
            "name": str(i) + ": " + joystick.get_name(),
            "obj": joystick
        }
        active_controllers.append(joystick_info)

    controller1_dropdown["values"] = [controller["name"] for controller in active_controllers]
    controller2_dropdown["values"] = [controller["name"] for controller in active_controllers]


# Initialize Pygame for controller input
pygame.init()
pygame.joystick.init()

udp_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)] # setup 4 different sockets for each ESP32
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # setup a broadcast socket for all ESP32s gamestate
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Create main application window
root = tk.Tk()
root.title("Robot Controller")

# Robot 1 Frame
frame1 = tk.LabelFrame(root, text="Robot 1 Control", padx=10, pady=10)
frame1.grid(row=0, column=0, padx=10, pady=10)

# Robot 2 Frame
frame2 = tk.LabelFrame(root, text="Robot 2 Control", padx=10, pady=10)
frame2.grid(row=0, column=2, padx=10, pady=10)

# Dropdown to select Robot 1
robot1_label = tk.Label(frame1, text="Select Robot:")
robot1_label.grid(row=0, column=0, padx=5, pady=5)
robot1_var = tk.StringVar(value="")
robot1_dropdown = ttk.Combobox(frame1, textvariable=robot1_var, values=[robot["name"] for robot in robots], state="readonly")
robot1_dropdown.grid(row=1, column=0, padx=5, pady=5)

# Dropdown to select USB Controller for Robot 1
controller1_label = tk.Label(frame1, text="Select USB Controller:")
controller1_label.grid(row=2, column=0, padx=5, pady=5)
controller1_var = tk.StringVar(value="")
controller1_dropdown = ttk.Combobox(frame1, textvariable=controller1_var, values=[controller["name"] for controller in active_controllers], state="readonly")
controller1_dropdown.grid(row=3, column=0, padx=5, pady=5)

# Button to connect Robot 1
connect1_button = tk.Button(frame1, text="Connect Robot 1", 
                            command=lambda: connect_robot(robot1_var.get(), controller1_var.get()))
connect1_button.grid(row=4, column=0, padx=5, pady=5)

# Dropdown to select Robot 2
robot2_label = tk.Label(frame2, text="Select Robot:")
robot2_label.grid(row=0, column=0, padx=5, pady=5)
robot2_var = tk.StringVar(value="")
robot2_dropdown = ttk.Combobox(frame2, textvariable=robot2_var, values=[robot["name"] for robot in robots], state="readonly")
robot2_dropdown.grid(row=1, column=0, padx=5, pady=5)

# Dropdown to select USB Controller for Robot 2
controller2_label = tk.Label(frame2, text="Select USB Controller:")
controller2_label.grid(row=2, column=0, padx=5, pady=5)
controller2_var = tk.StringVar(value="")
controller2_dropdown = ttk.Combobox(frame2, textvariable=controller2_var, values=[controller["name"] for controller in active_controllers], state="readonly")
controller2_dropdown.grid(row=3, column=0, padx=5, pady=5)

# Button to connect Robot 2
connect2_button = tk.Button(frame2, text="Connect Robot 2", 
                            command=lambda: connect_robot(robot2_var.get(), controller2_var.get()))
connect2_button.grid(row=4, column=0, padx=5, pady=5)

# Center Frame for toggle buttons
center_frame = tk.Frame(root, padx=10, pady=10)
center_frame.grid(row=0, column=1, padx=10, pady=10)

# Create buttons for Standby, Autonomy, and Teleoperation
buttons = {}
for i, mode in enumerate(button_order):
    button = tk.Button(center_frame, text=mode, width=20, command=lambda m=mode: toggle_button(buttons[m]))
    button.grid(row=i, column=0, padx=10, pady=10)
    buttons[mode] = button

# Refresh Controllers button
refresh_button = tk.Button(center_frame, text="Refresh Controllers", width=20, command=refresh_controllers)
refresh_button.grid(row=len(button_order), column=0, padx=10, pady=10)

# Start with the Standby button active
toggle_button(buttons["Standby"])

# Bind the spacebar key to toggle between buttons
root.bind('<space>', on_spacebar_press)

# refresh controllers a little later once UI has been created otherwise dropdowns break
refresh_controllers()

# Start threads for sending data (these will auto send udp packets while running our own thing)
Thread(target=send_controller_data, daemon=True).start()
Thread(target=broadcast_game_status, daemon=True).start()

# Start the Tkinter main loop
root.mainloop()

# Clean up sockets on exit
for sock in udp_sockets:
    sock.close()
broadcast_socket.close()