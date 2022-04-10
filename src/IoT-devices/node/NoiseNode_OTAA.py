""" FiPy OTAA Node compatible with the Fipy Noise Gateway """

from network import LoRa
import socket
import binascii
import struct
import time, utime

class NoiseNode:
    """
    Noise Node, set up by default for a Noise Gateway in OTAA mode.
    """

    def __init__(self, debug, app_eui, app_key, frequency, datarate):
        self.debug = debug
        self.mode = "OTAA"
        self.OTA_params = {'app_eui': app_eui,'app_key': app_key}
        self.lora = None
        self.frequency = frequency
        self.datarate = datarate

        self.dev_eui = None
        self.app_eui = None
        self.app_key = None

        self.s = None

    def start(self):
        self._log("Booting noisenode in " + self.mode + " mode")
        # initialize LoRa in LORAWAN mode.
        self.lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
        # erase previous lora settings in ram
        self.lora.nvram_erase()
        # create an OTA authentication params
        self.dev_eui = self.lora.mac()
        self.app_eui = self.OTA_params['app_eui']#binascii.unhexlify('70B3D57EF0003BFD')
        self.app_key = self.OTA_params['app_key']#binascii.unhexlify('36AB7625FE770B6881683B495300FFD6')
        # set the 3 default channels to the same frequency (must be before sending the OTAA join request)
        [self.lora.add_channel(i, frequency=self.frequency, dr_min=0, dr_max=5) for i in range(3)]
        # join a network using OTAA
        self.lora.join(activation=LoRa.OTAA, auth=(self.app_eui, self.app_key), timeout=0, dr=4)#config.LORA_NODE_DR)
        # wait until the module has joined the network
        while not self.lora.has_joined():
            time.sleep(2.5)
            self._log('Not joined yet...')
        self._log('Node joined the network')
        # remove all the non-default channels
        [self.lora.remove_channel(i) for i in range(3, 16)]
        # create a LoRa socket
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        # set the LoRaWAN data rate
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, self.datarate)
        # make the socket non-blocking
        self.s.setblocking(True)
        # save lora config
        self.lora.nvram_save()

    def _log(self, message, *args):
        """
        Outputs a log message to stdout.
        """
        if self.debug==True:
            print('[{:>10.3f}] {}'.format(
                utime.ticks_ms() / 1000,
                str(message).format(*args)
                ))

    def send_packet(self, payload=None, rx_ON=True):
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, self.datarate)
        self.s.setblocking(False)
        self.s.send(bytes([1, 2, 3]))
        if(rx_ON)
            self.s.settimeout(3.0) # configure a timeout value of 3 seconds
            try:
              rx_pkt = s.recv(64)   # get the packet received (if any)
              self._log(rx_pkt)
            except socket.timeout:
              self._log('No packet received')

    # def send_lorawan_packets(self, count=50):
    #     for i in range (count):
    #         pkt = b'PKT #' + bytes([i])
    #         print('Sending:', pkt)
    #         self.s.send(pkt)
    #         time.sleep(4)
    #         rx, port = self.s.recvfrom(256)
    #         if rx:
    #             print('Received: {}, on port: {}'.format(rx, port))
    #         time.sleep(20)
    # _LORA_PKG_FORMAT = "BB%ds"
    # _LORA_PKG_ACK_FORMAT = "BBB"
    # DEVICE_ID = 0x01
    #
    # def send_greetings(self):
    #     msg = "Hello, Device 1 Here"
    #     pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), DEVICE_ID, len(msg), msg)
    #     self.s.send(pkg)
    #
    #     # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
    #     waiting_ack = True
    #     self._log("opening rx slot")
    #     while(waiting_ack):
    #         recv_ack = self.s.recv(256)
    #         if (len(recv_ack) > 0):
    #             device_id, pkg_len, ack = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
    #             self._log(device_id)
    #             if (device_id == DEVICE_ID):
    #                 if (ack == 200):
    #                     waiting_ack = False
    #                     # If the uart = machine.UART(0, 115200) and os.dupterm(uart) are set in the boot.py this print should appear in the serial port
    #                     print("ACK")
    #                 else:
    #                     waiting_ack = False
    #                     # If the uart = machine.UART(0, 115200) and os.dupterm(uart) are set in the boot.py this print should appear in the serial port
    #                     print("Message Failed")
