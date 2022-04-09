"""Main code for a Noise-node sending LoRaWAN-packets in OTAA mode"""

import config_node as config
from NoiseNode_OTAA import NoiseNode

if __name__ == '__main__':
    noisenode = NoiseNode()
    noisenode.start()
    input('You may now press ENTER to enter the REPL') # REPL inputs
    #noisenode.send_lorawan_packets(count=2)
