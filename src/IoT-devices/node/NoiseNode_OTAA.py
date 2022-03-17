""" OTAA Node example compatible with the Fipy Noise Gateway """

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
        self.dev_eui = None
        self.app_eui = None
        self.app_key = None
        self.s = None

    def start(self):
        # initialize LoRa in LORAWAN mode.
        self.lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
        # create an OTA authentication params
        self.dev_eui = binascii.unhexlify('AABBCCDDEEFF7778')
        self.app_eui = binascii.unhexlify('70B3D57EF0003BFD')
        self.app_key = binascii.unhexlify('36AB7625FE770B6881683B495300FFD6')
        # set the 3 default channels to the same frequency (must be before sending the OTAA join request)
        self.lora.add_channel(0, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        self.lora.add_channel(1, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        self.lora.add_channel(2, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        # join a network using OTAA
        self.lora.join(activation=LoRa.OTAA, auth=(self.dev_eui, self.app_eui, self.app_key), timeout=0, dr=config.LORA_NODE_DR)
        # wait until the module has joined the network
        while not self.lora.has_joined():
            time.sleep(2.5)
            print('Not joined yet...')
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
