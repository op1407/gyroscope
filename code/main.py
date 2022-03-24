from ST7735 import TFT
from mpu6050 import MPU6050
from sysfont import sysfont
from machine import SPI,Pin, PWM
import time


# PINs
BL = 13 # Blacklight LED pin
power = Pin(12, Pin.IN, Pin.PULL_UP) # Button to turn the display on / off
recal = Pin(6, Pin.IN, Pin.PULL_UP)  # Button to flip image vertica / horizontal

# Display parameters
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=None)
tft=TFT(spi,16,17,18)
tft.initr()
tft.rgb(True)

pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(65535) 

# MPU-6050 Parameters
G = 9.8
mpu = MPU6050(1, 15, 14) #bus(1), SCL(GP15), SDA(GP14)
mpu.MPU_Init() #initialize the MPU6050
time.sleep(1)  #waiting for MPU6050 to work steadily


def main_gyroscope():

    while True:
        # Gyro configuration
        accel = mpu.MPU_Get_Accelerometer()
        
        if not power.value(): # Power ON
            if not recal.value(): # Switch turned / pressed  -->  Vertical
                tft.fillrect((64, 0), (64, 160), TFT.L_BLUE)
                tft.fillrect((0, 0), (64, 160), TFT.GREEN)
                up_down = accel[2]/16384
                left_right = accel[1]/16384
                
                pwm.duty_u16(65535)
                tilt = 64 + round(up_down * 64)
                slant_line_left = 64 - round(left_right * 64)
                slant_line_right = 64 + round(left_right * 64)
                left_end = (tilt + slant_line_left) - 64
                right_end = (tilt + slant_line_right) - 64
                
                # Display horizontal line
                for i in range(2): # Draw 2 lines to make the line appear thicker, second line is +1 pixel below the first
                    tft.line((left_end + i, 30), (right_end + i, 130), TFT.BLACK)
                time.sleep_ms(100)

            else: # Horizontal
                tft.fillrect((0, 0), (128, 80), TFT.L_BLUE)
                tft.fillrect((0, 80), (128, 80), TFT.GREEN)
                up_down = accel[2]/16384
                left_right = accel[0]/16384
                
                pwm.duty_u16(65535)
                tilt = 80 + round(up_down * 80)
                slant_line_left = 80 - round(left_right * 80)
                slant_line_right = 80 + round(left_right * 80)
                left_end = (tilt + slant_line_left) - 80
                right_end = (tilt + slant_line_right) - 80
                
                # Display horizontal line
                for i in range(2): # Draw 3 lines to make the line appear thicker, second line is +1 pixel below the first
                    tft.line((10, left_end + i), (118, right_end + i), TFT.BLACK)
                time.sleep_ms(100)
        else: # Power OFF
            pwm.duty_u16(0) # Backlight LED off
            

if __name__ == "__main__":
    main_gyroscope()