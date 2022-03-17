""" LoPy LoRaWAN Nano Gateway example usage """

import config_node as config
from NoiseNode_ABP import NoiseNode

if __name__ == '__main__':

    print("booting node")
    noisenode = NoiseNode()
    noisenode.start()
    noisenode.send_lorawan_packets(count=15)
