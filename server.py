#!/usr/bin/python3

import socket
import socketserver
import logging
import struct
import re
import datetime

SERVER_HOST = socket.gethostname()
SERVER_PORT = 8000
SERVER_LISTENERS = 5
SERVER_BUFFER_SIZE = 1024

MESSAGE_LOGGER = 'gpstracker.log'

imei_dict = {}


def p_load(imei, parm):
    imei_dict[imei] = datetime.datetime.now()
    return 'LOAD'


def p_heartbeat(imei):
    imei_dict[imei] = datetime.datetime.now()
    return 'ON'

TRACKER_PROTOCOL_RE = [
    (r'?P<p_load_0>##,imei:(?P<imei_0>\d+),(?P<parm_0>\w+);', p_load),
    (r'?P<p_heartbeat_1>(?P<imei_1>\d+)', p_heartbeat),
]

TRACKER_PROTOCOL = re.compile(r'(' +
                              r')|('.join(_re
                                          for _re, _f in TRACKER_PROTOCOL_RE) +
                              r')')


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
            str_data = str(data, 'utf8')
            terminate = data == b''
            logging.info("Recived:{0}".format(data))

            mat_data = TRACKER_PROTOCOL.match(str_data)
            if mat_data:
                tokens = {k: v
                          for k, v in mat_data.groupdict().items()
                          if v is not None}
                idx = int([k.split('_')[-1] for k in tokens][0])
                _re, _f = TRACKER_PROTOCOL_RE[idx]
                args = {k.split('_')[0]:v
                        for k,v in tokens.items()
                        if 'p_' != k[:2]}
                r = _f(**args)
                logging.info("Executed:{0}:{1}->{2}".format(_f, args, r))
                self.request.sendall(bytes(r + '\n', 'utf8'))
            else:
                logging.info("Not implemented:{0}".format(data))
                self.request.sendall(bytes('\n', 'utf8'))
        logging.info("Disconnection:{0}".format(self.server.socket))


if __name__ == '__main__':
    try:
        logging.basicConfig(filename=MESSAGE_LOGGER, level=logging.DEBUG)
        server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), GpsHandler)
        logging.info("Start serving:{0}".format(server))
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Pressed Ctrl+C. Stopping.')
        server.socket.close()

#
