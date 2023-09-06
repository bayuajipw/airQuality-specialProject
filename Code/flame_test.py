#!/usr/bin/python

import RPi.GPIO as GPIO
import time

# Set GPIO mode and pin number
GPIO.setmode(GPIO.BCM)
flame_sensor_pin = 21

# Setup GPIO pin
GPIO.setup(flame_sensor_pin, GPIO.IN)

# Main loop
while True:
	flame_detected = GPIO.input(flame_sensor_pin)

	if flame_detected:
		print("Flame detected!")
	else:
		print("No flame detected.")

	time.sleep(1)
