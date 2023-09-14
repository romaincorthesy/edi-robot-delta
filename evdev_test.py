#!/usr/bin/env python3

import evdev

# Define the device path for your mouse
device_path = "/dev/input/event0"

# Open the input device
device = evdev.InputDevice(device_path)

x = 0
y = 0

# Read mouse events
for event in device.read_loop():
    if event.type == evdev.ecodes.EV_REL:
        if event.code == evdev.ecodes.REL_X:
            x += event.value
            #print(f"Mouse X movement: {event.value}")
        elif event.code == evdev.ecodes.REL_Y:
            y += event.value
            #print(f"Mouse Y movement: {event.value}")
        print(f"Position : {x}, {y}")
