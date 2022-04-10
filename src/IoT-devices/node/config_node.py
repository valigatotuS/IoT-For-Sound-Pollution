""" FiPy LoRaWAN Noise Node configuration options """

import machine
import binascii

# debug mode (printing the node logs)
DEBUG = True

# LoRa settings for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5

# OTA parameters
APP_EUI = binascii.unhexlify('70B3D57EF0003BFD')
APP_KEY = binascii.unhexlify('36AB7625FE770B6881683B495300FFD6')
