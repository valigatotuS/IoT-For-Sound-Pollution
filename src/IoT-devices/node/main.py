""" Main code for a lora node tested on TTN with LoRaWAN, OTAA & ADR """

import config, time
from NoiseNode import NoiseNode

if __name__ == '__main__':
    noisenode = NoiseNode(
        debug             = config.DEBUG,
        lora_params       = config.LORA_PARAMETERS,
        lora_session_keys = config.LORA_SESSION_KEYS,
        deepsleep_time    = config.DEEPSLEEP_TIME,
        )

    # starting the LoRaWAN Noise Node
    noisenode._log("Starting Noise Node with id: %s" % noisenode.lora_session_keys['dev_eui'])
    noisenode.init_lora_radio()
    noisenode.join_network_server()

    if noisenode.debug:
        # Entering RPL (Read Evaluate Print Loop, interactive MicroPython prompt)
        input('Press ENTER to enter the REPL')

    else:
        # Sending noise level on regular interval via LoRa
        noisenode.collect_sensor_data() # analog reads
        noisenode.send_sensor_data()    # sending data, then entering deepsleep
