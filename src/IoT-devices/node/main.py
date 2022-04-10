"""Main code for a Noise-node sending LoRaWAN-packets in OTAA mode"""

import config_node as config
from NoiseNode_OTAA import NoiseNode

if __name__ == '__main__':
    noisenode = NoiseNode(
        debug = config.DEBUG,
        # OTA parameters
        app_eui = config.APP_EUI,
        app_key = config.APP_KEY,
        # LoRa parameters
        frequency = config.LORA_FREQUENCY,
        datarate = config.LORA_NODE_DR
        )

    noisenode.start()
    input('You may now press ENTER to enter the REPL') # REPL inputs
