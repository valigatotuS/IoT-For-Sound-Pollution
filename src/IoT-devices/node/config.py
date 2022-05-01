""" FiPy LoRaWAN Noise Node configuration options """

import binascii, struct
from network import LoRa

# debug mode (printing the node logs)
DEBUG = True

# LoRa settings
LORA_REGION = LoRa.EU868
LORA_CLASS = LoRa.CLASS_A
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5
LORA_MODE = LoRa.LORAWAN
LORAWAN_ACTIVATION_MODE = 'OTAA' # OTAA/ABP

# OTA keys
APP_EUI = binascii.unhexlify('70B3D57EF0003BFD')
APP_KEY = binascii.unhexlify('36AB7625FE770B6881683B495300FFD6')

# ABP keys
DEV_ADDR = struct.unpack(">l", binascii.unhexlify('260BF086'))[0]
DEV_EUI = None
NWK_SWKEY = binascii.unhexlify('3C74F4F40CAEA021303BC24284FCF3AF')
APP_SWKEY = binascii.unhexlify('0FFA7072CC6FF69A102A0F39BEB0880F')

# deepsleep
DEEPSLEEP_TIME = 0                      # 0 to disable deepsleep
# confirmed transmission (handshake)
CONFIRMED_TX = True