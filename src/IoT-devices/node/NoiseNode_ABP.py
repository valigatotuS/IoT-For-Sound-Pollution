""" ABP Node example compatible with the Fipy Noise Gateway """

from network import LoRa
import socket
import binascii
import struct
import time
import config_node as config

class NoiseNode:
    """
    Noise Node, set up by default for Noise Gateway in OTAA mode.
    """

    def __init__(self):
        self.lora = None
        self.dev_addr = None
        self.nwk_swkey = None
        self.swkey = None
        self.s = None

    def start(self):
        # initialize LoRa in LORAWAN mode.
        self.lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
        # create an ABP authentication params
        self.dev_addr = struct.unpack(">l", binascii.unhexlify('2601147D'))[0]
        self.nwk_swkey = binascii.unhexlify('3C74F4F40CAEA021303BC24284FCF3AF')
        self.app_swkey = binascii.unhexlify('0FFA7072CC6FF69A102A0F39BEB0880F')
        # set the 3 default channels to the same frequency (must be before sending the OTAA join request)
        self.lora.add_channel(0, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        self.lora.add_channel(1, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        self.lora.add_channel(2, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        # join a network using ABP (Activation By Personalization)
        self.lora.join(activation=LoRa.ABP, auth=(self.dev_addr, self.nwk_swkey, self.app_swkey))
        # remove all the non-default channels
        for i in range(3, 16):
            self.lora.remove_channel(i)
        # create a LoRa socket
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        # set the LoRaWAN data rate
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.LORA_NODE_DR)
        # make the socket non-blocking
        self.s.setblocking(False)
        time.sleep(5.0)

    def send_lorawan_packets(self, count=50):
        for i in range (count):
            pkt = b'PKT #' + bytes([i])
            print('Sending:', pkt)
            self.s.send(pkt)
            time.sleep(4)
            rx, port = self.s.recvfrom(256)
            if rx:
                print('Received: {}, on port: {}'.format(rx, port))
            time.sleep(20)
