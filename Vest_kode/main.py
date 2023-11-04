#her laver vi vores mai
from machine import Pin, ADC, UART, I2C
import sys, uselect
from time import sleep
from imu import MPU6050
import time
import umqtt_robust2 as mqtt
from gpio_lcd import GpioLcd
from sys import exit
from gps_bare_minimum import GPS_Minimum

#bat måler
bat = ADC(Pin(39, Pin.IN),atten=3)
bat.atten(ADC.ATTN_11DB)
bat.width(ADC.WIDTH_12BIT)

#imu
i2c = I2C(0)
imu = MPU6050(i2c)

#lcd
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32),
              d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=2, num_columns=16)

#gps
gps_port = 2
gps_speed = 9600
uart = UART(gps_port, gps_speed) 
gps = GPS_Minimum(uart)

#other 
end = 0
bat_posent_div = 0
bat_posent_qual = 0
gang = 0
taklinger = 0
takel_count_up = 0
takel_count_down = 0
takling = 0
gemensnits_speed_data = 0
gemensnits_speed_tal = 0
gemensnits_speed_data = 0
top_hastihed = 0
slide = 0


def get_adafruit_gps():
    speed = lat = lon = None # Opretter variabler med None som værdi
    if gps.receive_nmea_data():
        # hvis der er kommet end bruggbar værdi på alle der skal anvendes
        if gps.get_speed() != -999 and gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            # gemmer returværdier fra metodekald i variabler
            speed =str(gps.get_speed())
            lat = str(gps.get_latitude())
            lon = str(gps.get_longitude())
            # returnerer data med adafruit gps format
            return speed + "," + lat + "," + lon + "," + "0.0"
        else: # hvis ikke både hastighed, latitude og longtitude er korrekte 
            print(f"GPS data to adafruit not valid:\nspeed: {speed}\nlatitude: {lat}\nlongtitude: {lon}")
            return False
    else:
        return False

print('klar')
while True:
    pot_val = bat.read()
    spaending = pot_val * (3.5 / 4096)
    bat_posent_div = 100*((spaending-2.0434782609)/(0.8173913042999996)) + bat_posent_div
    bat_posent_qual = bat_posent_qual + 1
    
    gps_data = get_adafruit_gps()
    
    acceleration = imu.accel
    gyroscope = imu.gyro  
    
    if abs(acceleration.x) > 0.8:
        if (acceleration.x > 0):
            "The x axis points upwards"
            takel_count_down = takel_count_down + 1
        else:
            "The x axis points downwards"
            takel_count_down = takel_count_down + 1

    if abs(acceleration.y) > 0.8:
        if (acceleration.y > 0):
            "The y axis points upwards"
            takel_count_down = takel_count_down + 1
        else:
            "The y axis points downwards"
            takel_count_down = takel_count_down + 1

    if abs(acceleration.z) > 0.8:
        if (acceleration.z > 0):
            "The z axis points upwards"
            takel_count_down = 0
            takel_count_up = takel_count_up + 1
        else:
            "The z axis points downwards"
            takel_count_down = takel_count_down + 1
    
    if takel_count_down >= 10 and takling == 0:
        taklinger = taklinger + 1
        takling = 1
        takel_count_up = 0
        
    if takel_count_up > 20 and takling == 1:
        takling = 0
        takel_count_down = 0
    
    start = time.time()
    sleep(0.1)
    if start - end >= 3:
        bat_posent = int(bat_posent_div / bat_posent_qual)
        bat_posent_div, bat_posent_qual = 0,0
        lcd.clear() #clear den siste besked fra lcdet
        lcd.putstr(f'tacklet:{taklinger}  {bat_posent}%')
        print(f'bat:{bat_posent}')
        print(f'takling:{taklinger}')
        end = time.time()
        if gang == 0:
            if gps_data: # hvis der er korrekt data så send til adafruit
                mqtt.web_print(gps_data, 'gruppeotte/feeds/iot-feed/csv')
                gemensnits_speed_data = gemensnits_speed_data + gps.get_speed()
                gemensnits_speed_tal = gemensnits_speed_tal + 1
                if top_hastihed < gps.get_speed():
                    top_hastihed = gps.get_speed()
            print('fdfd')
        if gang == 1:
            mqtt.web_print(gps.get_speed(), 'gruppeotte/feeds/speed/csv')
            print('holollow')
            
        if gang == 2:
            mqtt.web_print(bat_posent, 'gruppeotte/feeds/bat/csv')
            gang = -1
        gang = gang + 1
    
    if mqtt.besked == 'stop':
        break
    
    if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
        mqtt.besked = ""
            
    mqtt.sync_with_adafruitIO()
    
gemensnits_speed = "{:.4f}".format(gemensnits_speed_data/gemensnits_speed_tal)
top_hastihed = "{:.2f}".format(top_hastihed)
top_hastihed_dis = f'Top fart:{top_hastihed}'
gemensnits_speed_dis = f'Gns.fart:{gemensnits_speed}'
info = [top_hastihed_dis, gemensnits_speed_dis]
while True:
    lcd.clear() #clear den siste besked fra lcdet
    lcd.putstr(f'Tacklet:{taklinger}  {bat_posent}%\n{info[slide]}')
    sleep(5)
    slide = 1 - slide
    print(info[slide])
    print(slide)
    