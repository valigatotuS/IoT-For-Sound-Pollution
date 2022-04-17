"""Main code for a Noise-node sending LoRaWAN-packets in OTAA mode"""

import config_node as config
from NoiseNode import NoiseNode

if __name__ == '__main__':
    noisenode = NoiseNode(
        debug = config.DEBUG,
        # LoRa parameters
        activation_mode = config.LORAWAN_ACTIVATION_MODE,
        frequency = config.LORA_FREQUENCY,
        datarate = config.LORA_NODE_DR,
        # Activation keys (OTA & ABP)
        activation_keys = {'app_eui': config.APP_EUI,'app_key': config.APP_KEY, 'dev_addr': config.DEV_ADDR, 'dev_eui': config.DEV_EUI, 'nwk_swkey': config.NWK_SWKEY, 'app_swkey': config.APP_SWKEY}
        )

    noisenode.start()
    input('You may now press ENTER to enter the REPL') # REPL inputs
