# Gyroscope v03
# 05/07/2022
# (c) McLocvin

### Minor modifications made: 03/11/2024

from ST7735 import TFT
from mpu6050 import MPU6050
from sysfont import sysfont
from machine import SPI, Pin, PWM, ADC
import time
import math


# RGB LED
pins = [20, 19, 21]
freq_num = 10000
pwm1 = PWM(Pin(pins[0]))
pwm2 = PWM(Pin(pins[1]))
pwm3 = PWM(Pin(pins[2]))
pwm1.freq(freq_num)
pwm2.freq(freq_num)
pwm3.freq(freq_num)

# Battery charger setup
vsys = ADC(29)
charging = Pin(24, Pin.IN)
conversion_factor = (3 * 3.3) / 65535
refresh_rate = 2.5 # Battery status refresh rate in minutes

full_battery = 4.1
empty_battery = 3.40

# PINs
BL = 13 # Backlight LED pin
recal = Pin(6, Pin.IN, Pin.PULL_UP)  # Button to flip image vertical / horizontal

# Display parameters
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=None)
tft=TFT(spi,16,17,18)
tft.initr()
tft.rgb(True)

pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(65535)

# MPU-6050 Parameters
G = 9.81
mpu = MPU6050(1, 15, 14)
mpu.MPU_Init()

# Show startup message (No need for this, just for the kicks...)
# (has to have at least 1 second delay for the MPU6050 to start properly)
tft.fill(TFT.BLACK)
tft.text((0, 0), "Initializing", TFT.WHITE, sysfont, 1)
time.sleep(0.3)
tft.text((0, 0), "Initializing.", TFT.WHITE, sysfont, 1)
time.sleep(0.3)
tft.text((0, 0), "Initializing..", TFT.WHITE, sysfont, 1)
time.sleep(0.3)
tft.text((0, 0), "Initializing...", TFT.WHITE, sysfont, 1)
time.sleep(0.3)

def main_gyroscope():
    good_battery = True
    # Creating empty lists for future use
    up_down = []
    left_right = []
    global avg_batt
    avg_batt = []
    # Settings re_cal values so program will show absolute zero before recalibrating
    accel_1 = -0.031
    accel_2 = -0.2
    
    while good_battery:
        # Gyro configuration
        accel = mpu.MPU_Get_Accelerometer()
        
        #Battery configuration
        avg_batt.append(vsys.read_u16())
        
        if charging.value() == 1:
            set_color(65535, 65535, 65535)
        else:
            if len(avg_batt) == refresh_rate * 60 * 10:
                avg_vsys = math.floor(sum(avg_batt) / len(avg_batt))
                voltage = avg_vsys * conversion_factor
                battery_status()
        
        if not recal.value(): # Set current level to zero level (calibrate)
            tft.fill(TFT.BLACK)
            tft.text((0,0), str("Calibrating..."), TFT.WHITE, sysfont, 1)
            accel_2 =  accel[2]/16384
            accel_1 = accel[1]/16384
            time.sleep(1)
            tft.text((0,0), str("Device calibrated!"), TFT.WHITE, sysfont, 1)
            time.sleep(2)

        else:
            tft.fillrect((0, 0), (128, 80), TFT.L_BLUE)
            tft.fillrect((0, 80), (128, 80), TFT.GREEN)
            up_down.append(accel[2]/16384 - accel_2)
            left_right.append(accel[1]/16384 - accel_1)
            if len(up_down) == 2:
                up_down = round(sum(up_down) / len(up_down), 3) # Rounds to 3 decimals
                left_right = round(sum(left_right) / len(left_right), 3)
                pwm.duty_u16(65535)
                tilt = 80 + round(up_down * 80)
                slant_line_left = 80 + round(left_right * 80)
                slant_line_right = 80 - round(left_right * 80)
                left_end = (tilt + slant_line_left) - 80
                right_end = (tilt + slant_line_right) - 80
            
                # Display horizontal line
                for i in range(2): # Draw 2 lines to make the line appear thicker, second line is +1 pixel below the first
                    tft.line((10, left_end + i), (118, right_end + i), TFT.BLACK)
                    
                up_down = []
                left_right = []                
            
            time.sleep(0.1)
            
def set_color(r, g, b): # Set the RGD LED color
            pwm1.duty_u16(r)
            pwm2.duty_u16(g)
            pwm3.duty_u16(b)
            
def low_battery(): # If battery level < 5%, stop program and blink RED light
    tft.fill(TFT.BLACK)
    tft.text((0, 0), str("Low battery!"), TFT.WHITE, sysfont, 1)
    tft.text((0, 10), str("Recharge device..."), TFT.WHITE, sysfont, 1)
    while True:
        set_color(0, 65535, 65535)
        time.sleep(0.5)
        set_color(65535, 65535, 65535)
        time.sleep(0.5)
        
def battery_status():
    ### TODO :
    ### Make several IF-ELIF -statements. Return the result? (might not be necessary)
    ### Use this function also when USB cable is unplugged.
    ### avg_batt needs to be a global variable
    percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
    
    ###
    # For debugging only
    # You need to have an USB cable WITHOUT +5V in order for these to work properly
    # While charging, battery voltage around 4.8V and precentage around 200%
    print(f"Voltage: {voltage:.2f}v")
    print(f"Percentage: {percentage:.0f} %")
    ###
    
    if percentage > 90:
        set_color(65535, 0, 65535) # Show GREEN light, over 90%
        avg_batt = []
    elif percentage > 50 and percentage < 90: # Show BLUE light, 25% - 90%
        set_color(65535, 65535, 0)
        avg_batt = []
    elif percentage > 25 and percentage < 50: # Show YELLOW light, 25% - 90%
        set_color(32767, 32767, 65535)
        avg_batt = []
    elif percentage > 5 and percentage < 25: # Shows RED light, 5% - 25%
        set_color(0, 65535, 65535)
        avg_batt = []
    else:
        set_color(65535, 65535, 65535) # LED off, battery level under 5%
        good_battery = False
        avg_batt = []
        low_battery()
    

if __name__ == "__main__":
    # Reading the battery level to set the LED to right color
    # Otherwise it would take a long time for the light to turn on
    voltage = vsys.read_u16() * conversion_factor
    percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))    
    battery_status()
        
    main_gyroscope()
