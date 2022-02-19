from machine import Timer
from machine import Pin
import pycom, time

pycom.heartbeat(False)
while True:
    print("White")
    pycom.rgbled(0x7600AF)
    time.sleep(2)
    print("Red")
    pycom.rgbled(0x7f0000)
    time.sleep(2)
