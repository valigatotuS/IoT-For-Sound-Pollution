""" FiPy LoRaWAN Noise Node configuration options """

import machine, binascii, struct

# debug mode (printing the node logs)
DEBUG = True

# LoRa settings for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5
LORAWAN_ACTIVATION_MODE = 'OTAA'

# OTA keys
APP_EUI = binascii.unhexlify('70B3D57EF0003BFD')
APP_KEY = binascii.unhexlify('36AB7625FE770B6881683B495300FFD6')

# ABP keys
DEV_ADDR = struct.unpack(">l", binascii.unhexlify('260BF086'))[0]
DEV_EUI = None
NWK_SWKEY = binascii.unhexlify('3C74F4F40CAEA021303BC24284FCF3AF')
APP_SWKEY = binascii.unhexlify('0FFA7072CC6FF69A102A0F39BEB0880F')
