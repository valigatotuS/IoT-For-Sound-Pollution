"""Main code for a Noise-node sending LoRaWAN-packets in OTAA mode"""

import config
from NoiseNode import NoiseNode

if __name__ == '__main__':
    noisenode = NoiseNode(
        debug           = config.DEBUG,
        # LoRa parameters
        lora_mode       = config.LORA_MODE,
        lora_region     = config.LORA_REGION,
        lora_class      = config.LORA_CLASS,
        activation_mode = config.LORAWAN_ACTIVATION_MODE,
        frequency       = config.LORA_FREQUENCY,
        datarate        = config.LORA_NODE_DR,
        # Activation keys (OTA & ABP)
        activation_keys = {'app_eui': config.APP_EUI,'app_key': config.APP_KEY, 'dev_addr': config.DEV_ADDR, 'dev_eui': config.DEV_EUI, 'nwk_swkey': config.NWK_SWKEY, 'app_swkey': config.APP_SWKEY},
        # Deepsleep time
        deepsleep_time  = config.DEEPSLEEP_TIME, 
        # Confirmed transmission
        confirmed_tx    = config.CONFIRMED_TX
        )

    noisenode.start()       # starting the lorawan node
    # noisenode.simulate_dB_transmission()

    if noisenode.debug: input('You may now press ENTER to enter the REPL') # REPL inputs
    else:               noisenode.simulate_dB_transmission()
    
