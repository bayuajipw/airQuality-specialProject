import sys
from time import sleep
import RPi.GPIO as GPIO
import busio
from mq2 import MQ2

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


mq2 = MQ2()
    
while True:
    perc1 = mq2.MQPercentage()
    perc1['SMOKE'] = round(perc1['SMOKE'], 2)

    if perc1['SMOKE'] is not None:
        sys.stdout.write('Smoke : %.2f ppm\n' %(perc1['SMOKE']))
    else:
        print("Gagal Memperoleh Data")
