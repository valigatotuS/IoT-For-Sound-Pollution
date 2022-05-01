""" FiPy OTAA Node compatible with the Fipy Noise Gateway """

from network import LoRa
import socket
import binascii
import struct
import time, utime, uos, machine
import pycom

class NoiseNode:
    """
    IoT-node.

    Setup:
        * µC:                   FiPy
        * Communication:        LoRa
    """

    def __init__(self, debug, lora_mode, lora_region, lora_class, activation_mode, frequency, datarate, activation_keys, confirmed_tx, deepsleep_time):
        pycom.heartbeat(False)
        self.debug          = debug
        self.activation_keys= activation_keys
        self.lora_config    = {"mode": lora_mode, "region": lora_region, "class": lora_class, "activation_mode":activation_mode, "freq":frequency, "dr":datarate}
        self.lora           = None
        self.lora_socket    = None
        self.confirmed_tx   = confirmed_tx
        self.deepsleep_time = deepsleep_time
        self.tx_stats       = {"tx_conf":0, "tx_consecutive_fails":0}


    def start(self):
        self._log("Booting noisenode in " + self.lora_config["activation_mode"] + " mode")
        self.lora = LoRa(
            mode        =self.lora_config["mode"],
            region      =self.lora_config["region"],
            device_class=self.lora_config["class"],
                # adr         =True, # not configured because lopy gateway only listens on one channel
            )
        self.add_channels()                                                 # setting the LoRa channels
        self.lora.nvram_restore()                                               # will restore lora connection and erase nvram lora 
            
        if (not self.lora.has_joined) or (self.deepsleep_time==0):    
            self.join_network_server()                                          # joining the network server with self.activation_mode
        else:
            self._log("lora settings restored with nvram")
            self.lora.nvram_save()                                              # saving lora config

        self.create_socket()                                                    # creating lora socket

    def join_network_server(self):
        """
        Joins the network-server over lora.
        """
        self.status_led('joining')
        # join a network
        if self.lora_config["activation_mode"] == 'OTAA':
            self._log('Node is joining the network server...')
            self.lora.join(activation=LoRa.OTAA, auth=(self.activation_keys['app_eui'], self.activation_keys['app_key']), timeout=0, dr=4) #implement DR var
    
            while not self.lora.has_joined():                                   # wait until the module has joined the network
                time.sleep(1)
                self._log('\tNot joined yet...')
            self._log('Node joined the network')
            self.lora.nvram_erase()  
            self.lora.nvram_save()                                              # saving lora config
            self.tx_stats["tx_consecutive_fails"] = 0
            self.status_led('joined')
            time.sleep(3)

        elif self.lora_config["activation_mode"] == 'ABP':
            self.lora.join(activation=LoRa.ABP, auth=(self.activation_keys['dev_addr'], self.activation_keys['nwk_swkey'], self.activation_keys['app_swkey']), timeout=0, dr=4)


    def create_socket(self):
        """
        Creates and configures the lora-socket.
        """
        self.lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)             # creating the lora-socket
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.lora_config["dr"])     # setting the right socket-parameters

        if self.confirmed_tx:
            self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)  # asking confirmation of transmitted packets to the network server

        self.lora.callback(trigger=( LoRa.RX_PACKET_EVENT |             # lora event handler for transmission/reception/transmission_fail
            LoRa.TX_PACKET_EVENT |
            LoRa.TX_FAILED_EVENT  ), handler=self.lora_callback)    

        self.lora_socket.setblocking(False)                                           # opening the socket

    def add_channels(self):
        [self.lora.add_channel(i, frequency=self.lora_config["freq"], dr_min=0, dr_max=5) for i in range(3)]  # setting the 3 default channels to the same frequency (must be before sending the OTAA join request)
        [self.lora.remove_channel(i) for i in range(3, 16)]                 # removing all the non-default channels

    def lora_callback(self, lora):
        """
        Callback for lora-events.
        """
        events = self.lora.events()
        if events & LoRa.RX_PACKET_EVENT:                                   # raised for every received packet
            if self.lora_socket is not None:
                frame, port = self.lora_socket.recvfrom(512)
                self._log("Packet reception:\n\tport: %s, frame:%s" % (port, frame))

        if events & LoRa.TX_PACKET_EVENT:                                   # raised as soon as the packet transmission cycle ends
            self._log("Transmission ended:\n\ttx_time_on_air: %s ms, @dr %s, trials: %s" % (self.lora.stats().tx_time_on_air, self.lora.stats().sftx, self.lora.stats().tx_trials))
            if self.confirmed_tx: 
                self.tx_stats["tx_conf"] += 1
                self.tx_stats["tx_consecutive_fails"] = 0
            if self.deepsleep_time > 0: 
                self.deepsleep(self.deepsleep_time*1000)

        if events & LoRa.TX_FAILED_EVENT:                                   # raised after the number of tx_retries configured have been performed and no ack is received
            self._log("sending Failed")
            self.tx_stats["tx_consecutive_fails"] += 1
            self._log("Transmission fail:\n\t tx_stats: confirmed_packets:%i, consecutive_fails:%i" % (self.tx_stats["tx_conf"], self.tx_stats["tx_consecutive_fails"]))
            if ((self.tx_stats["tx_consecutive_fails"] >= 5) and (self.confirmed_tx)):
                 self.join_network_server()


    def send_uplink(self, pkt='a'):
        """
        Sends a packet via LoRa.
        """
        try:
            self.status_led('sending')
            self._log('Sending packet...')
            self.lora_socket.send(pkt)
        except Exception as e:
            self._log(e)
            #self.join_network_server()

    def status_led(self, mode:str):
        """
        Blinks internal led based on status.
        """
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
        Outputs a log message to console.
        """
        if self.debug==True:
            print('[{:>10.3f}] {}'.format(
                utime.ticks_ms() / 1000,
                str(message).format(*args)
                ))

    def array2packet(self, array:list):
        pkt = struct.pack('>%sb' % (len(array)), *array)
        return pkt

    def deepsleep(self, time:int):
        self._log("Start deepsleep...")
        machine.deepsleep(time)    

#--------------- IN DEVELOPMENT -----------------------------------------------------------------------------#

    def simulate_dB_transmission(self):
        self._log("Starting dB transmission")
        data = 0
        while True:
            data = self.sensor_data_dB(sound_level=data)
            pkt  = self.array2packet([data])
            self.send_uplink(pkt)
            time.sleep(25)

    def sensor_data_dB(self, sound_level):
        """
        Return sound-level in dB from micro. (dummy-test)
        """
        self._log('Recolting dummy sensor data (sound-level)...')
        data = (sound_level + 1) % 10      # pass sensor implementation...
        return data

    def simulate_fft_transmission(self, delay=20):
        while True:
            data = self.sensor_data_fft()
            pkt  = self.array2packet(data)
            self.send_uplink(pkt)
            time.sleep(delay) # implement non blocking

    def sensor_data_fft(self):
        """
        Return sound-spectrum-analysis from micro. (dummy test)
        """
        self._log('Recolting dummy sensor data (fft)...')
        data = [uos.urandom(1)[0] for i in range(20)]      # pass sensor implementation...
        return data

    def simulate_packetloss(self, count=5, delay=20):
        self._log("Starting packet-loss test (count: %i, delay: %i)" % (count, delay))
        self.deepsleep_time = 0
        data = 0
        self.tx_stats["tx_conf"] = 0
        for i in range(count):
            data = self.sensor_data_dB(sound_level=data)
            pkt  = self.array2packet([data])
            self.send_uplink(pkt)
            time.sleep(delay) 
        self._log("%i/%i packets were succesfully sent & confirmed" % (self.tx_stats["tx_conf"], count))

#--------------- OLD CODE -----------------------------------------------------------------------------#
    def simulate_sensor_data_transmission_v2(self):
        i = 10
        while True:
            self._log('Recolting dummy sensor data...')
            i = (i + 1) % 10 # dummy simulation
            data = [i]
            pkt = struct.pack('>%sb' % (len(data)), *data)
            self.send_uplink(pkt)
            time.sleep(20)

    def send_packet(self, payload='A', rx_ON=True):
        self.status_led('sending')
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.lora_config['dr'])
        self.lora_socket.setblocking(False)
        self._log('Sending packet...')
        self.lora_socket.send(payload) # payload size-limit is 242 bytes long
        if(rx_ON):
            self.lora_socket.settimeout(8) # configure a timeout value for rx slot in TTN
            try:
                rx_pkt = self.lora_socket.recv(64)   # get the packet received (if any)
                self._log('Received packet: ' + str(rx_pkt))
                self._log(self.lora.stats())
            except socket.timeout:
                self._log('No packet received')
        #self.lora_socket.setblocking(True)

    _LORA_PKG_FORMAT = "BB%ds"
    _LORA_PKG_ACK_FORMAT = "BBB"

    def send_confirmed_packet(self):
            self.status_led('sending')
            self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.lora_config['dr'])
            self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
            self.lora_socket.setblocking(False)
            self._log('Sending packet...')
            self.lora_socket.send('222') # payload size-limit is 242 bytes long

            self.lora_socket.settimeout(20) # configure a timeout value for rx slot in TTN
            try:
                time.sleep(4)
                rx_pkt = self.lora_socket.recv(64)   # get the packet received (if any)
                self._log('Received packet: ' + str(rx_pkt))
                self._log(self.lora.stats())
            except socket.timeout:
                self._log('No packet received')

    def send_sound(self):
        self._log('Recolting sound sensor data...')
        data = [1,2,3,4,1,2,3,4]
        pkt = struct.pack('>%sb' % (len(data)), *data)
        self.send_packet(pkt, rx_ON=False)

    def simulate_sensor_data_transmission(self):
        i = 10
        while True:
            self._log('Recolting dummy sensor data...')
            i = (i + 1) % 10 # dummy simulation
            data = [i]
            pkt = struct.pack('>%sb' % (len(data)), *data)
            self.send_packet(pkt, rx_ON=False)
            time.sleep(20)

    def send_confp(self):
        # set the LoRaWAN data rate
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
        # msg are confirmed at the FMS level
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
        # make the socket non blocking y default
        self.lora_socket.setblocking(False)

        self.lora.callback(trigger=( LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT | LoRa.TX_FAILED_EVENT  ), handler=self.lora_cb)

        time.sleep(4) # this timer is important and caused me some trouble ...

        for i in range(0, 1000):
            pkt = struct.pack('>H', i)
            print('Sending:', pkt)
            self.lora_socket.send(pkt)
            time.sleep(20)

    def prepare_socket_sending(self):

        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)             # set the LoRaWAN data rate
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)   # msg are confirmed at the FMS level
        self.lora_socket.setblocking(False)                                       # make the socket non blocking y default
        # self.lora.init(mode=LoRa.LORAWAN, region=LoRa.EU868, device_class=LoRa.CLASS_A, adr=True, tx_retries=5, sf=7, bandwidth=self.bandwidth)
        # self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self.lora_cb)
        self.lora.callback(trigger=( LoRa.RX_PACKET_EVENT |
                                LoRa.TX_PACKET_EVENT |
                                LoRa.TX_FAILED_EVENT  ), handler=self.lora_cb)

        time.sleep(4)                                                   # this timer is important and caused me some trouble ...
