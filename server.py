#!/usr/bin/python3

import socket
import socketserver
import logging
import struct

SERVER_HOST = socket.gethostname()
SERVER_PORT = 8000
SERVER_LISTENERS = 5
SERVER_BUFFER_SIZE = 1024

MESSAGE_LOGGER = 'gpstracker.log'

TRACKER_MESSAGE_CHUNKS = "<2s11s8s11s6s1s10s1s10s5s6s6s8s1s8s1s"
TRACKER_MESSAGE_KEYS = ['protocol_version',
                        'device_id',
                        'fixed',
                        'device_id_rep',
                        'date',
                        'gps_valid',
                        'latitude',
                        'ignored_a',
                        'longitude',
                        'speed',
                        'time',
                        'cardinal_heading',
                        'device_status',
                        'ignored_b',
                        'odometer',
                        'eol']

tracker_message_chunks = struct.Struct(TRACKER_MESSAGE_CHUNKS)


class GpsHandler(socketserver.BaseRequestHandler):
    def handle(self):
        terminate = False
        logging.info("Connection:{0}".format(self.server.socket))
        while not terminate:
            data = self.request.recv(SERVER_BUFFER_SIZE)
            terminate = data == b''
            logging.info("Recived:{0}".format(data))
            if not terminate and len(data) == tracker_message_chunks.size:
                data_struct = dict(zip(TRACKER_MESSAGE_KEYS,
                                       tracker_message_chunks.unpack(data)))
                logging.info("Struct:{0}".format(data_struct))
        logging.info("Disconnection:{0}".format(self.server.socket))


if __name__ == '__main__':
    logging.basicConfig(filename=MESSAGE_LOGGER, level=logging.DEBUG)
    server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), GpsHandler)
    server.serve_forever()
