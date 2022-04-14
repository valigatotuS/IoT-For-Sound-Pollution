""" FiPy LoRaWAN Noise Gateway configuration options """

import machine
import ubinascii

WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()
# Set  the Gateway ID to be the first 3 bytes of MAC address + 'FFFE' + last 3 bytes of MAC address
GATEWAY_ID = WIFI_MAC[:6] + "FFFE" + WIFI_MAC[6:12]

# server settings
SERVER = 'eu1.cloud.thethings.network'
PORT = 1700

# clock settings (synchronization with Network Time Protocol)
NTP = "pool.ntp.org"
NTP_PERIOD_S = 3600

# wifi settings
WIFI_SSID = 'VOO-294307'#'WiFi-2.4-1C18'#
WIFI_PASS = 'FUWGERFQ'#'wnuxdz5j32k4j'#

# LoRa settings for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5

# debug mode
DEBUG = True
