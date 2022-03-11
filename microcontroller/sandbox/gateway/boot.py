from network import WLAN
import ubinascii
wl = WLAN()
ubinascii.hexlify(wl.mac()[0])[:6] + 'FFFE' + ubinascii.hexlify(wl.mac()[0])[6:]
