""" FiPy LoRaWAN Noise Node configuration options """

import binascii, struct
from network import LoRa

# debug mode (printing the node logs)
DEBUG = True

# LoRa settings
LORA_REGION     = LoRa.EU868            # Europe
LORA_CLASS      = LoRa.CLASS_A          # 2 rx slots after tx 
LORA_CHANNELS   = {0:868100000, 1:868300000, 2:868500000, 3:867100000, 4:867300000, 5:867500000, 6:867700000, 7:867900000, 8:868800000}
LORA_FREQUENCY  = LORA_CHANNELS[0]       
LORA_NODE_DR    = 5                     # "SF7BW125" 
LORA_MODE       = LoRa.LORAWAN          # v 1.0.2
LORAWAN_ACTIVATION_MODE = 'OTAA'        # OTAA/ABP

# OTA keys
APP_EUI = '70B3D57EF0003BFD'            # mac adress...
APP_KEY = '36AB7625FE770B6881683B495300FFD6' 

# ABP keys
DEV_ADDR = struct.unpack(">l", binascii.unhexlify('260BF086'))[0]
DEV_EUI = None
NWK_SWKEY = binascii.unhexlify('3C74F4F40CAEA021303BC24284FCF3AF')
APP_SWKEY = binascii.unhexlify('0FFA7072CC6FF69A102A0F39BEB0880F')

# deepsleep
DEEPSLEEP_TIME = 0                  # 0 to disable deepsleep
# confirmed transmission (handshake)
CONFIRMED_TX = True