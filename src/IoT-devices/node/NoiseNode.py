""" FiPy OTAA Node tested with the Fipy as Noise Gateway """

from network import LoRa, LTE, WLAN, Bluetooth
import socket
import binascii
from binascii import unhexlify as uhex
import struct
import time, utime, uos, machine
import pycom

class NoiseNode:
    """
    LoRa(WAN) node reporting sound
    """

    def __init__(self, debug, lora_params, lora_session_keys, deepsleep_time):
        # disabling unuseful background processes, limiting power-consumtion
        pycom.heartbeat(False)      # stopping internal led pulse
        LTE().deinit()              # disabling cellular radio
        WLAN().deinit()             # disabling wifi radio
        Bluetooth().deinit()        # disabling bluetooth radio
        # properties
        self.debug              = debug
        self.lora_session_keys  = lora_session_keys
        self.lora_params        = lora_params
        self.lora               = None          # LoRa-object
        self.lora_socket        = None          # networking-endpoint, bound to IP-adress and port-nr
        self.deepsleep_time     = deepsleep_time
        self.tx_stats           = {"tx_conf":0, "tx_consecutive_fails":0} # transmission stats
        self.sensor_data        = {}

    def start(self):
        self._log("Starting Noise Node with id: %s" % self.lora_session_keys['app_eui'])
        self.init_lora_radio()
        self.join_network_server()

    def init_lora_radio(self):
        """ Initialises the lora radio by configuring the LoRa-object and socket. """

        self._log('Configuring LoRa radio with %s mode on channel %iMHz with DR%i' % (self.lora_params['activation'], self.lora_params['channel'], self.lora_params['dr']))
        self.lora = LoRa(
            mode         = self.lora_params["mode"],
            region       = self.lora_params["region"],
            device_class = self.lora_params["class"],
            adr          = self.lora_params["adr"],
            tx_retries   = self.lora_params["retries"]
            )
        self.init_channels()        # adding & removing the right LoRa channels
        self.init_socket()          # configuring the LoRa parameters and setting up the socket

    def join_network_server(self):
        """ Joining network server with keys in ABP/OTAA. """

        if (machine.reset_cause() == machine.DEEPSLEEP_RESET) and (self.tx_stats["tx_consecutive_fails"] <= 2):
            self.lora.nvram_restore()                       # restoring lora join-session (appeui, appkey, framecounter) and erasing from ram
            self._log("lora settings restored with nvram")
            self.lora.nvram_save()                          # saving lora join-session in the ram

        # joining through OTAA
        elif self.lora_params["activation"] == 'OTAA':
            self._log('Joining the network server...', status="joining")
            try:
                self.lora.join(
                    activation = LoRa.OTAA,
                    auth       = (uhex(self.lora_session_keys['app_eui']), uhex(self.lora_session_keys['app_key'])),
                    timeout    = 20_000,
                    dr         = 5
                    )

            except OSError as os_e:
                self._log(os_e)
                self.deepsleep(0) # resetting board

            finally:
                self._log('Node joined the network', status="joined")
                self.tx_stats["tx_consecutive_fails"] = 0

            if not self.lora.has_joined():  self.deepsleep(0)

        # joining through ABP
        elif self.lora_params["activation_mode"] == 'ABP':
            self.lora.join(
                activation = LoRa.ABP,
                auth       = (self.lora_session_keys['dev_addr'], self.lora_session_keys['nwk_swkey'], self.lora_session_keys['app_swkey']),
                timeout    = 20,
                dr         = 5
                )

    def init_socket(self):
        """ Initialise and configures the lora-socket. """

        self.lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)                                   # initialising the raw lora-socket
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.lora_params["dr"])                  # setting the lora socket data rate
        self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, self.lora_params["confirmed_tx"]) # setting transmission-confirmation (asking handshake)

        self.lora.callback(trigger=(                # lora event handler for transmission/reception/transmission_fail
            LoRa.RX_PACKET_EVENT |
            LoRa.TX_PACKET_EVENT |
            LoRa.TX_FAILED_EVENT  ), handler=self.lora_callback)

        #self.lora_socket.setblocking(False)                                         # opening the socket

    def init_channels(self):
        """ Removes and adds the right LoRa channels. """

        [self.lora.add_channel(i, frequency=self.lora_params["channel"], dr_min=0, dr_max=5) for i in range(3)]  # setting the 3 default channels to the same frequency (must be before sending the OTAA join request) this is also removing the other channels
        #[self.lora.remove_channel(i) for i in range(3, 16)]                         # removing all the non-default channels

    def lora_callback(self, lora:LoRa):
        """ Callback for lora-events. """

        events = self.lora.events()

        # raised for every received packet
        if events & LoRa.RX_PACKET_EVENT:
            if self.lora_socket is not None:
                frame, port = self.lora_socket.recvfrom(512)
                self._log("Packet reception:\n\tport: %s, frame:%s" % (port, frame), 'reception')

        # raised as soon as the packet transmission cycle ends
        if events & LoRa.TX_PACKET_EVENT:
            self._log("Transmission ended:\n\ttx_time_on_air: %s ms, @dr %s, trials: %s" % (self.lora.stats().tx_time_on_air, self.lora.stats().sftx, self.lora.stats().tx_trials))
            if self.lora_params["confirmed_tx"]:
                self._log("Reception of confirmed downlink", "confirmed_downlink")
                self.tx_stats["tx_conf"] += 1
                self.tx_stats["tx_consecutive_fails"] = 0
            if self.deepsleep_time > 0:
                self.deepsleep(self.deepsleep_time*1000)

        # raised after the number of tx_retries configured have been performed and no ack is received
        if events & LoRa.TX_FAILED_EVENT:
            self._log("sending Failed")
            self.tx_stats["tx_consecutive_fails"] += 1
            self._log("Transmission fail:\n\t tx_stats: confirmed_packets:%i, consecutive_fails:%i" % (self.tx_stats["tx_conf"], self.tx_stats["tx_consecutive_fails"]))
            if ((self.tx_stats["tx_consecutive_fails"] >= 2) and (self.lora_params['confirmed_tx'])):
                 self.join_network_server()

    def send_uplink(self, pkt='a'):
        """ Sends a packet via LoRa. """

        try:
            self._log('Sending packet...', status="sending")
            self.lora_socket.send(pkt)  # sending packet with LoRa chip <sx1276>

        except Exception as e:          # maybe add function to catch when payload is to large
            self._log(e)
            self.reset()                # resetting board if error occurs while sending packet

    def _log(self, message:str, status="", *args):
        """ Outputs a time-stamped log message to console and blinks internal led according status. """

        if self.debug==False:
            return

        print('[{:>10.3f}] {}'.format(
                utime.ticks_ms() / 1000,        # printing clock ticks in seconds
                str(message).format(*args)      # printing the message
                ))

        if status != "":
            self.status_led(status)

    def status_led(self, mode:str):
        """ Blinks internal led based on status. """

        if self.debug:
            if mode == 'joining':
                self.blink_led('red')
            elif mode == 'joined':
                self.blink_led('green', 1)
            elif mode == 'sending':
                for i in range(3): self.blink_led('blue', 0.2)
            elif mode == 'confirmed_downlink':
                self.blink_led('green', 0.5)
            elif mode == 'reception':
                for i in range(3): self.blink_led('yellow', 0.2)

    def blink_led(self, color:str, delay=0):
        """ Blinks internal led with color during x time. """

        colors = {'red': 0xff0000, 'green': 0x00ff00, 'blue': 0x0000ff, 'yellow':0x7f7f00} #RGBY
        pycom.rgbled(colors[color])
        if time:
            time.sleep(delay)
            pycom.rgbled(False)
            time.sleep(delay)

    def array2packet(self, array:list) -> list:
        """ Converts int array to binaries """
        pkt = struct.pack('>%sb' % (len(array)), *array)
        return pkt

    def deepsleep(self, time:int):
        """ Enters deep-sleep modus and saving lora join-session beforehands """

        self.lora.nvram_save()          # saving lora join-session (appeui, appkey, framecounter), important to save just before sleep, otherwise framecounter may be incorrect !
        self._log("Start deepsleep...")
        machine.deepsleep(time)

    def reset(self):
        machine.reset()

#--------------- IN DEVELOPMENT -----------------------------------------------------------------------------#

    def simulate_dB_transmission(self, delay=25):
        self._log("Starting dB transmission")
        data = 0
        while True:
            data = self.sensor_data_dB(sound_level=data)
            pkt  = self.array2packet([data])
            self.send_uplink(pkt)
            time.sleep(delay)

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
        self._log("Node configuration")
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
    # def simulate_sensor_data_transmission_v2(self):
    #     i = 10
    #     while True:
    #         self._log('Recolting dummy sensor data...')
    #         i = (i + 1) % 10 # dummy simulation
    #         data = [i]
    #         pkt = struct.pack('>%sb' % (len(data)), *data)
    #         self.send_uplink(pkt)
    #         time.sleep(20)

    # def send_packet(self, payload='A', rx_ON=True):
    #     self.status_led('sending')
    #     self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.lora_params['dr'])
    #     self.lora_socket.setblocking(False)
    #     self._log('Sending packet...')
    #     self.lora_socket.send(payload) # payload size-limit is 242 bytes long
    #     if(rx_ON):
    #         self.lora_socket.settimeout(8) # configure a timeout value for rx slot in TTN
    #         try:
    #             rx_pkt = self.lora_socket.recv(64)   # get the packet received (if any)
    #             self._log('Received packet: ' + str(rx_pkt))
    #             self._log(self.lora.stats())
    #         except socket.timeout:
    #             self._log('No packet received')
    #     #self.lora_socket.setblocking(True)

    # _LORA_PKG_FORMAT = "BB%ds"
    # _LORA_PKG_ACK_FORMAT = "BBB"

    # def send_confirmed_packet(self):
    #         self.status_led('sending')
    #         self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.lora_params['dr'])
    #         self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
    #         self.lora_socket.setblocking(False)
    #         self._log('Sending packet...')
    #         self.lora_socket.send('222') # payload size-limit is 242 bytes long

    #         self.lora_socket.settimeout(20) # configure a timeout value for rx slot in TTN
    #         try:
    #             time.sleep(4)
    #             rx_pkt = self.lora_socket.recv(64)   # get the packet received (if any)
    #             self._log('Received packet: ' + str(rx_pkt))
    #             self._log(self.lora.stats())
    #         except socket.timeout:
    #             self._log('No packet received')

    # def send_sound(self):
    #     self._log('Recolting sound sensor data...')
    #     data = [1,2,3,4,1,2,3,4]
    #     pkt = struct.pack('>%sb' % (len(data)), *data)
    #     self.send_packet(pkt, rx_ON=False)

    # def simulate_sensor_data_transmission(self):
    #     i = 10
    #     while True:
    #         self._log('Recolting dummy sensor data...')
    #         i = (i + 1) % 10 # dummy simulation
    #         data = [i]
    #         pkt = struct.pack('>%sb' % (len(data)), *data)
    #         self.send_packet(pkt, rx_ON=False)
    #         time.sleep(20)

    # def send_confp(self):
    #     # set the LoRaWAN data rate
    #     self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    #     # msg are confirmed at the FMS level
    #     self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
    #     # make the socket non blocking y default
    #     self.lora_socket.setblocking(False)

    #     self.lora.callback(trigger=( LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT | LoRa.TX_FAILED_EVENT  ), handler=self.lora_cb)

    #     time.sleep(4) # this timer is important and caused me some trouble ...

    #     for i in range(0, 1000):
    #         pkt = struct.pack('>H', i)
    #         print('Sending:', pkt)
    #         self.lora_socket.send(pkt)
    #         time.sleep(20)

    # def prepare_socket_sending(self):

    #     self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)             # set the LoRaWAN data rate
    #     self.lora_socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)   # msg are confirmed at the FMS level
    #     self.lora_socket.setblocking(False)                                       # make the socket non blocking y default
    #     # self.lora.init(mode=LoRa.LORAWAN, region=LoRa.EU868, device_class=LoRa.CLASS_A, adr=True, tx_retries=5, sf=7, bandwidth=self.bandwidth)
    #     # self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self.lora_cb)
    #     self.lora.callback(trigger=( LoRa.RX_PACKET_EVENT |
    #                             LoRa.TX_PACKET_EVENT |
    #                             LoRa.TX_FAILED_EVENT  ), handler=self.lora_cb)

    #     time.sleep(4)                                                   # this timer is important and caused me some trouble ...
