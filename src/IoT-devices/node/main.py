""" Main code for a lora node tested on TTN with LoRaWAN, OTAA & ADR """

import config
from NoiseNode import NoiseNode

if __name__ == '__main__':
    noisenode = NoiseNode(
        debug             = config.DEBUG,
        lora_params       = config.LORA_PARAMETERS,
        lora_session_keys = config.LORA_SESSION_KEYS,
        deepsleep_time    = config.DEEPSLEEP_TIME,
        )

    # starting the LoRaWAN Noise Node
    noisenode.start()

    if noisenode.debug:
        # Entering RPL (Read Evaluate Print Loop, interactive MicroPython prompt)
        noisenode.simulate_dB_transmission()#input('Press ENTER to enter the REPL')
    else:
        # Sending noise level on regular interval via LoRa (dummy data)
        noisenode.simulate_dB_transmission()
