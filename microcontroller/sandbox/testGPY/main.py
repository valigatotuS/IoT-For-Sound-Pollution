import pycom
import time 
print("GPY rebooted")

while True:
    pycom.rgbled(0x011111111)
    time.sleep(1)
    pycom.rgbled(0x000000000)
    time.sleep(1)
    