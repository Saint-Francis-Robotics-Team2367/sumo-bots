import tkinter as tk
from tkinter import ttk

# Dummy options for robot and USB controllers
robots = ["Robot A", "Robot B", "Robot C"]
usb_controllers = ["Controller 1", "Controller 2", "Controller 3"]

# To track the active button
active_button = None
button_order = ["Standby", "Autonomy", "Teleoperation"]

# Function to connect robot (for future extension)
def connect_robot(robot, controller):
    print(f"Connected {robot} to {controller}")

# Function to toggle button states
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
robot1_var = tk.StringVar(value=robots[0])
robot1_dropdown = ttk.Combobox(frame1, textvariable=robot1_var, values=robots, state="readonly")
robot1_dropdown.grid(row=1, column=0, padx=5, pady=5)

# Dropdown to select USB Controller for Robot 1
controller1_label = tk.Label(frame1, text="Select USB Controller:")
controller1_label.grid(row=2, column=0, padx=5, pady=5)
controller1_var = tk.StringVar(value=usb_controllers[0])
controller1_dropdown = ttk.Combobox(frame1, textvariable=controller1_var, values=usb_controllers, state="readonly")
controller1_dropdown.grid(row=3, column=0, padx=5, pady=5)

# Button to connect Robot 1
connect1_button = tk.Button(frame1, text="Connect Robot 1", 
                            command=lambda: connect_robot(robot1_var.get(), controller1_var.get()))
connect1_button.grid(row=4, column=0, padx=5, pady=5)

# Dropdown to select Robot 2
robot2_label = tk.Label(frame2, text="Select Robot:")
robot2_label.grid(row=0, column=0, padx=5, pady=5)
robot2_var = tk.StringVar(value=robots[0])
robot2_dropdown = ttk.Combobox(frame2, textvariable=robot2_var, values=robots, state="readonly")
robot2_dropdown.grid(row=1, column=0, padx=5, pady=5)

# Dropdown to select USB Controller for Robot 2
controller2_label = tk.Label(frame2, text="Select USB Controller:")
controller2_label.grid(row=2, column=0, padx=5, pady=5)
controller2_var = tk.StringVar(value=usb_controllers[0])
controller2_dropdown = ttk.Combobox(frame2, textvariable=controller2_var, values=usb_controllers, state="readonly")
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

# Start with the Standby button active
toggle_button(buttons["Standby"])

# Bind the spacebar key to toggle between buttons
root.bind('<space>', on_spacebar_press)

# Start the Tkinter main loop
root.mainloop()
