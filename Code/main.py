import sys
from time import sleep
import RPi.GPIO as GPIO
import wiringpi
import Adafruit_DHT
import RPLCD as RPLCD
import busio
from RPLCD.i2c import CharLCD
from numpy import median
from mcp3008 import MCP3008
from mq2 import MQ2
from sharpPM10 import sharpPM10
import paho.mqtt.client as mqtt
import json

# MQTT
Host = 'broker.mqtt-dashboard.com'
client = mqtt.Client()
client.connect(Host, 1883, 60)
client.loop_start()

# Status Lab
Y = "Kondisi Sehat"
N = "Kondisi Tidak sehat"
A = "Terdeteksi"
P = "Tidak Terdeteksi"

# Deklarasi PIN
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Berdasarkan GPIO

# Deklarasi Buzzer
Buzzer = 19
GPIO.setup(Buzzer, GPIO.OUT, initial=GPIO.LOW)
D = 1  # delay buzzer

# Deklarasi Sensor Suhu & Kelembapan
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 26

# Deklarasi Sensor Gas
mq2 = MQ2()

# Deklarasi Sensor Debu
sharp_pin = 23
sharp_channel = 4
wiringpi.wiringPiSetupGpio() 
ADC = MCP3008(0, 0)
sharpPM10 = sharpPM10(led_pin=sharp_pin, pm10_pin=sharp_channel, adc=ADC)

# Deklarasi Flame Sensor
Flame = 21
GPIO.setup(Flame, GPIO.IN)

# Deklarasi Fan Control
Fan = 17
GPIO.setup(Fan, GPIO.OUT, initial=GPIO.LOW)

# Deklarasi Water Pump Control
WaterPump = 27
GPIO.setup(WaterPump, GPIO.OUT, initial=GPIO.LOW)

# Penampilan Data Pada LCD
lcd = CharLCD('PCF8574', 0x27)
lcd.cursor_pos = (0, 0)
lcd.write_string('--------------------')
lcd.cursor_pos = (1, 1)
lcd.write_string('LaboratoriumBengkel')
lcd.cursor_pos = (2, 1)
lcd.write_string('Poltek Nuklir-BRIN')
lcd.cursor_pos = (3, 0)
lcd.write_string('--------------------')
sleep(1.5)
lcd.clear()

# Main Loop
while True:
    # Pembacaan Suhu & Kelembapan
    Kelembapan, Suhu = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    Kelembapan = round(Kelembapan, 2)
    Suhu = round(Suhu, 2)

    # Pembacaan Gas Berbahaya
    perc1 = mq2.MQPercentage()
    perc2 = sharpPM10.read()
    perc1['CO'] = round(perc1['CO'], 2)
    perc1['SMOKE'] = round(perc1['SMOKE'], 2)
    perc2 = round(perc2, 2)
    
    if perc1['CO'] is not None and perc1['SMOKE'] is not None and perc2 is not None and Kelembapan is not None and Suhu is not None:
        print('Suhu: {0:0.1f} C Kelembapan: {1:0.1f}%'.format(Suhu, Kelembapan))
        sys.stdout.write('CO: %.2f ppm, Asap: %.2f ug/m3, Debu: %.2f ug/m3, ' % (perc1['CO'], perc1['SMOKE'], perc2))
        # Program Untuk Membunyikan Buzzer:
        # Suhu Ruangan
        if Suhu < 18 or Suhu > 30:
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(D)
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Sh', json.dumps(N), 1)  # publish
        elif Suhu >= 18 or Suhu <= 30:
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Sh', json.dumps(Y), 1)  # publish
        else:
            pass
        # Kelembapan Ruangan
        if Kelembapan < 40 or Kelembapan > 70:
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(D)
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Kel', json.dumps(N), 1)  # publish
        elif Kelembapan >= 40 or Kelembapan <= 70:
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Kel', json.dumps(Y), 1)  # publish
        else:
            pass
        # Gas Berbahaya
        if perc1['CO'] > 25:
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(D)
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('CO', json.dumps(N), 1)  # publish
        elif perc1['CO'] <= 25:
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('CO', json.dumps(Y), 1)  # publish
        else:
            pass
        if perc1['SMOKE'] > 25:
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(D)
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('SMOKE', json.dumps(N), 1)  # publish
        elif perc1['SMOKE'] <= 25:
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('SMOKE', json.dumps(Y), 1)  # publish
        else:
            pass
        # Debu
        if perc2 > 50:
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(D)
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Debu', json.dumps(N), 1)  # publish
        elif perc2 <= 50:
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Debu', json.dumps(Y), 1)  # publish
        else:
            pass

        # Flame Sensor
        flame_state = GPIO.input(Flame)
        if flame_state == GPIO.HIGH:
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(D)
            GPIO.output(Buzzer, GPIO.LOW)
            client.publish('Flame', json.dumps(A), 1)  # publish
            flame_status = "Ada"
            print('Api: Ada\n')
        else:
            client.publish('Flame', json.dumps(P), 1)  # publish
            flame_status = "Tiada"
            print('Api: Tiada\n')
            
        # Water Pump Control
        if perc1['SMOKE'] > 25 or flame_state == GPIO.HIGH:
            GPIO.output(WaterPump, GPIO.HIGH)
            sleep(D)
        else:
            GPIO.output(WaterPump, GPIO.LOW)
            
        # Fan Control
        if Suhu > 25 or perc1['CO'] > 25 or perc1['SMOKE'] > 25 or perc2 > 50:
            GPIO.output(Fan, GPIO.HIGH)
            sleep(D)
        else:
            GPIO.output(Fan, GPIO.LOW)
            
        # Penampilan Data Pada LCD
        lcd.cursor_pos = (0, 0)
        lcd.write_string('---Kadar Gas(ppm)---')
        lcd.cursor_pos = (1, 0)
        lcd.write_string('Api: ' + flame_status.ljust(16))
        lcd.cursor_pos = (2, 0)
        lcd.write_string('Tmp: {0:.0f}C'.format(Suhu))
        lcd.cursor_pos = (3, 0)
        lcd.write_string('Hum: {0:.0f}%'.format(Kelembapan))
        lcd.cursor_pos = (1, 11)
        lcd.write_string('Debu: %.0f' % perc2)
        lcd.cursor_pos = (2, 11)
        lcd.write_string('CO  : %.1f' % perc1['CO'])
        lcd.cursor_pos = (3, 11)
        lcd.write_string('Asap: %.1f' % perc1['SMOKE'])

        # Penampilan Data Pada UI Node-RED
        client.publish('Sh1',json.dumps(Suhu), 1)
        client.publish('Kel1', json.dumps(Kelembapan), 1)
        client.publish('MQ2a', json.dumps(perc1['CO']), 1)
        client.publish('MQ2b', json.dumps(perc1['SMOKE']), 1)
        client.publish('GP2Y', json.dumps(perc2), 1)

    else:
        print("Gagal Memperoleh Data")

client.loop_stop()
client.disconnect()
