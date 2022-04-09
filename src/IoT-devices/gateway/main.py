""" LoPy LoRaWAN Nano Gateway example usage """

import config_TTN as config
from NoiseGateway import NoiseGateway

if __name__ == '__main__':
    noisegw = NoiseGateway(
        id=config.GATEWAY_ID,
        frequency=config.LORA_FREQUENCY,
        datarate=config.LORA_GW_DR,
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASS,
        server=config.SERVER,
        port=config.PORT,
        ntp_server=config.NTP,
        ntp_period=config.NTP_PERIOD_S
        )

    noisegw.start()
    noisegw._log('You may now press ENTER to enter the REPL')
    input() # REPL inputs
