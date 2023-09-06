#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

# Set GPIO mode and pin numbers
GPIO.setmode(GPIO.BCM)
relay_pins = [17, 27]  # Example relay control pins

# Setup GPIO pins
GPIO.setup(relay_pins, GPIO.OUT)

# Function to control the relays
def control_relay(relay_index, state):
    GPIO.output(relay_pins[relay_index], state)

# Main loop
while True:
    # Turn on relay 1, turn off relay 2
    control_relay(0, GPIO.HIGH)
    control_relay(1, GPIO.LOW)
    print("Relay 1 ON, Relay 2 OFF")
    time.sleep(2)

    # Turn off relay 1, turn on relay 2
    control_relay(0, GPIO.LOW)
    control_relay(1, GPIO.HIGH)
    print("Relay 1 OFF, Relay 2 ON")
    time.sleep(2)