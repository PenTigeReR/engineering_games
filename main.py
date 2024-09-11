import time
import bluetooth
from ble_advertising import advertising_payload
from machine import SoftI2C, PWM, Pin
from MX1508 import *
from tcs34725 import *
from time import sleep
from neopixel import NeoPixel
from ble_led import *

from micropython import const

turn_speed = 2

arrow_position = 77

arrow_servo = PWM(Pin(19, mode=Pin.OUT))
take_servo = PWM(Pin(23, mode=Pin.OUT))
arrow_servo.freq(50)
take_servo.freq(50)

left_motor = MX1508(Pin(32), Pin(33))
right_motor = MX1508(Pin(25), Pin(26))

ble = bluetooth.BLE()
uart = BLEUART(ble) 

i2c_bus = SoftI2C(sda = Pin(21), scl = Pin(22))
sensor = TCS34725(i2c = i2c_bus)

sensor.integration_time(1000)
sensor.gain(60)
sensor.active(True)
time.sleep_ms(500)

led = NeoPixel(Pin(17), 1)

message = [0, 0, 0, 0, 0]

#print(rgb_to_hsv(sensor.read(True)))


while True:
    
    def on_rx():
        global message, arrow_position, turn_speed
        message = list(map(int ,uart.read().decode().rstrip('\x00').split("$")))
        for i in range(4):
            if i in range(2):
                message[i] = int(message[i]) / 175
            elif i==3:
                #message[i] = int(int(message[i])*12  + 77)
                message[i] = int(int(message[i])*25 + 77)
            elif i==2:
                arrow_position = min(max(int(message[i])*turn_speed  + arrow_position, 10), 110)
        message[2] = arrow_position
        print(message)
            
    uart.irq(handler=on_rx)
    
    if(message[4]== 1):
        #led[0] = (255,0,0,)
        #led.write()
        
        print('a')
        
        colour = 'repeat'
        colour_read = sensor.read(True)
        colour_read = html_rgb(colour_read)
        
        print(colour_read)
        
        hsv = rgb_to_hsv(colour_read)
        
        print(hsv)
        
        colour_read = tuple(hsv_to_rgb([hsv[0], hsv[1], min(hsv[2]*2, 1)]))
        
        led[0] = tuple(hsv_to_rgb([hsv[0], min(hsv[1]*1.3, 1), hsv[2]*0.8]))
        #print(html_rgb(colour_read))
        
#         if hsv[0] < 45:
#             if hsv[1] < 30:
#                 if hsv[2] > 50:
#                     colour = 'black'
#                     led[0] = (0,0,0)
#                 else:
#                     colour = 'white'
#                     led[0] = (255,255,255)
#             else:
#                 colour = 'red'
#                 led[0] = (100,0,0)
#         elif 45 < hsv[0] < 90:
#             colour = 'yellow'
#             led[0] = (100,100,0)
#         elif 90 < hsv[0] < 140:
#             colour = 'green'
#             led[0] = (0,100,0)
#         elif 140 < hsv[0] < 200:
#             colour = 'blue'
#             led[0] = (0,0,100)
#         elif 200 < hsv[0] < 300:
#             colour = 'purplr'
#             led[0] = (100,0,100)
        
        uart.write('$'+'$'.join(str(x) for x in colour_read)+'$')
        led.write()
        
    
    arrow_servo.duty(round(int(message[2])))
    take_servo.duty(int(message[3]))
    left_motor.move(message[0])
    right_motor.move(message[1])
    
    time.sleep_ms(20)

    




