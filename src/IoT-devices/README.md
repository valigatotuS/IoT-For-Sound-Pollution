# IoT devices

## single-channel gateway
The single-channel gateway listens on one channel at a specific datarate and do not need an extra expansion board. The script is derived from the pycom/libraries.

## multi-channel gateway
The multi-channel gateway listens to all 8 channels at all SF's. The script is provided by pycom and configuration file by TTN.

## Node 
The main work of this project was to write the node's code. The code is totally written in MicroPython and make the use of the Pycom's libraries for using the active protocols on the FiPy board, essentially the network module. Our code is divided in three python script's : main, config and NoiseNode. 

- The Configuration file defining the LoRa parameters and session keys
- The NoiseNode class defining our node as an callable object
- The main file running our code 

___________________________________________________________________________________________________________________
___________________________________________________________________________________________________________________

## Left to do

- spelling check                            (later)
- resultaten invoegen:                
    - batterij uit testen 24ua 120m         (in-process...)
    - range testen zonder adr               (reporting...)
    - gnu radio for different sf's          (reporting...)
    - sensor implementatie                  (reporing...)
- gateway hfst reformuleren (single/multi)  (in-process...)
- conclusie formuleren                      (in-process...)
    - tekortkomingen en problemen
    - future work : spi sensor, private network with Chirpstack, more node/gateways in network

