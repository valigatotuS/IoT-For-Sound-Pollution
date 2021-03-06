""" FiPy OTAA Node compatible with the Fipy Noise Gateway """

from network import LoRa
import socket
import binascii
import struct
import time, utime
import pycom

class NoiseNode:
    """
    Noise Node, set up by default for a Noise Gateway in OTAA mode.
    """

    def __init__(self, debug, activation_mode, frequency, datarate, activation_keys):
        pycom.heartbeat(False)
        self.debug = debug
        self.activation_mode = activation_mode
        self.activation_keys = activation_keys
        self.lora = None
        self.frequency = frequency
        self.datarate = datarate
        self.s = None

    def start(self):
        self._log("Booting noisenode in " + self.activation_mode + " mode")

        self.lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)  # initialize LoRa in LORAWAN mode.
        self.lora.nvram_erase()                                 # erase previous lora settings in ram
        self.add_channels()                                     # setting the LoRa channels
        self.join_network_server()                              # joining the network server with self.activation_mode
        self.create_socket()                                    # creating lora socket
        self.lora.nvram_save()                                  # saving lora config

    def join_network_server(self):
        self.status_led('joining')
        # join a network
        if self.activation_mode == 'OTAA':
            self.lora.join(activation=LoRa.OTAA, auth=(self.activation_keys['app_eui'], self.activation_keys['app_key']), timeout=0, dr=4)#config.LORA_NODE_DR)

            # wait until the module has joined the network
            while not self.lora.has_joined():
                time.sleep(3)
                self._log('Not joined yet...')
            self._log('Node joined the network')
            self.status_led('joined')
            time.sleep(3)

        elif self.activation_mode == 'ABP':
            self.lora.join(activation=LoRa.ABP, auth=(self.activation_keys['dev_addr'], self.activation_keys['nwk_swkey'], self.activation_keys['app_swkey']), timeout=0, dr=4)


    def create_socket(self):
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, self.datarate)
        self.s.setblocking(True)

    def add_channels(self):
        [self.lora.add_channel(i, frequency=self.frequency, dr_min=0, dr_max=5) for i in range(3)]  # setting the 3 default channels to the same frequency (must be before sending the OTAA join request)
        [self.lora.remove_channel(i) for i in range(3, 16)]     # removing all the non-default channels

    def status_led(self, mode:str):
        if self.debug:
            if mode == 'joining':
                pycom.rgbled(0xff0000) #red
            elif mode == 'joined':
                pycom.rgbled(0x00ff00) #green
                time.sleep(0.5)
                pycom.rgbled(False)
            elif mode == 'sending':
                for i in range(3):
                    pycom.rgbled(0x0000ff) #blue
                    time.sleep(0.1)
                    pycom.rgbled(False)
                    time.sleep(0.1)


    def _log(self, message, *args):
        """
        Outputs a log message to stdout.
        """
        if self.debug==True:
            print('[{:>10.3f}] {}'.format(
                utime.ticks_ms() / 1000,
                str(message).format(*args)
                ))

    def send_packet(self, payload='A', rx_ON=True):
        self.status_led('sending')
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, self.datarate)
        self.s.setblocking(False)
        self._log('Sending packet...')
        self.s.send(payload) # payload size-limit is 242 bytes long
        if(rx_ON):
            self.s.settimeout(8) # configure a timeout value for rx slot in TTN
            try:
                rx_pkt = self.s.recv(64)   # get the packet received (if any)
                self._log('Received packet: ' + str(rx_pkt))
                self._log(self.lora.stats())
            except socket.timeout:
                self._log('No packet received')
        #self.s.setblocking(True)

    def send_sound(self):
        self._log('Recolting sound sensor data...')
        data = [1,2,3,4,1,2,3,4]
        pkt = struct.pack('>%sb' % (len(data)), *data)
        self.send_packet(pkt, rx_ON=False)

    def simulate_sensor_data_transmission(self):
        i = 11
        while True:
            self._log('Recolting dummy sensor data...')
            i = (i + 1) % 10 # dummy simulation
            data = [i]
            pkt = struct.pack('>%sb' % (len(data)), *data)
            self.send_packet(pkt, rx_ON=False)
            time.sleep(60)

    def lora_cb(self, lora):
        events = self.lora.events()
        if events & LoRa.RX_PACKET_EVENT:                               # raised for every received packet
            if self.s is not None:
                frame, port = self.s.recvfrom(512)
                self._log("port: %s, frame:%s" % (port, frame))

        if events & LoRa.TX_PACKET_EVENT:                               # raised as soon as the packet transmission cycle ends
            self._log("tx_time_on_air: %s ms, @dr %s, trials: %s" % (self.lora.stats().tx_time_on_air, self.lora.stats().sftx, self.lora.stats().tx_trials))

        if events & LoRa.TX_FAILED_EVENT:                               # raised after the number of tx_retries configured have been performed and no ack is received
            self._log("sending Failed")

    def prepare_socket_sending(self):

        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)             # set the LoRaWAN data rate
        self.s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)   # msg are confirmed at the FMS level
        self.s.setblocking(False)                                       # make the socket non blocking y default
        # self.lora.init(mode=LoRa.LORAWAN, region=LoRa.EU868, device_class=LoRa.CLASS_A, adr=True, tx_retries=5, sf=7, bandwidth=self.bandwidth)
        # self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self.lora_cb)
        self.lora.callback(trigger=( LoRa.RX_PACKET_EVENT |
                                LoRa.TX_PACKET_EVENT |
                                LoRa.TX_FAILED_EVENT  ), handler=self.lora_cb)

        time.sleep(4)                                                   # this timer is important and caused me some trouble ...



    def _send_up_link(self, pkt):
        """
        Transmits a downlink message over LoRa.
        """
        self.lora.init(
            mode=LoRa.LORAWAN,
            region=LoRa.EU868,
            frequency=self.frequency,
            bandwidth=LoRa.BW_125KHZ,
            sf=7,
            preamble=8,
            coding_rate=LoRa.CODING_4_5,
            tx_iq=True,
            tx_retries=5
            )
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, self.datarate)
        self.s.setblocking(False)
        time.sleep(4)
        self._log('Sending packet...')
        self.status_led('sending')
        self.s.send(pkt) # payload size-limit is 242 bytes long


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
