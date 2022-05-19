""" FiPy LoRaWAN Noise Gateway configuration options """

import machine
import ubinascii

WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()
# Set  the Gateway ID to be the first 3 bytes of MAC address + 'FFFE' + last 3 bytes of MAC address
GATEWAY_ID = WIFI_MAC[:6] + "FFFE" + WIFI_MAC[6:12]

# server settings
SERVER = '192.168.1.101'
PORT = 1700

# clock settings (synchronization with Network Time Protocol)
NTP = "pool.ntp.org"
NTP_PERIOD_S = 3600

# wifi settings
WIFI_SSID = 'SateliteVQ'    #'WiFi-2.4-1C18'#'VOO-294307'#
WIFI_PASS = '12345678'      #'wnuxdz5j32k4j'#'FUWGERFQ'#

# LoRa settings for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5
