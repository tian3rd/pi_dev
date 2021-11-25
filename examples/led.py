from gpiozero import LED
from time import sleep
led = LED(25)

while True:
    
    led.on()
    # led.off()
    sleep(1)
    led.off()
    sleep(1)