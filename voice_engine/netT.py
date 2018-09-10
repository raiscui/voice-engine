# -*- coding: utf-8 -*-

import numpy as np
import sys

from .element import Element
import threading
if sys.version_info[0] < 3:
    import Queue as queue
else:
    import queue
import socket
import time
import logging
import os
import stat
logger = logging.getLogger(__name__)


class DisconnectException(Exception):
    pass


class NetT(Element):
    def __init__(self):
        super(NetT, self).__init__()
        logger.debug("netT init")

        self.done = False
        self.conn = None
        self.sock = None
        self.lock = threading.Lock()    # protect self.sock object
        self.queue = queue.Queue()

        self.tcpSocket = "/tmp/echo1.sock"

        if os.path.exists(self.tcpSocket):
            try:
                os.unlink(self.tcpSocket)
            except OSError:
                logging.error("Could not unlink socket %s", self.tcpSocket)
                raise

        try:
            with self.lock:
                self.sock = socket.socket(
                    socket.AF_UNIX, socket.SOCK_STREAM)
                # socket.setdefaulttimeout(60)
                self.sock.setblocking(0)
                # self.sock.connect(self.tcpSocket)
                self.sock.bind(self.tcpSocket)
                self.sock.listen(1)
                logger.warning("Listening...")
        except socket.error, msg:
            logger.error(
                "Error when connect to the socket: {}".format(msg))
            raise
        except socket.timeout:
            logger.error('Timeout when connect to the socket')
            raise
        print('netT connected')

    def start(self):
        if os.path.exists(self.tcpSocket):
            os.chmod(self.tcpSocket, stat.S_IRWXO)
        print("netT start")
        self.done = False
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        # self.run()

    def run(self):
        loggerRun = logging.getLogger(__name__+".run")

        while not self.done:
            try:
                # with self.lock:
                while (not self.conn):
                    # print('w')

                    with self.lock:
                        conn, _ = self.sock.accept()
                        if (conn):
                            if (self.conn):
                                self.conn.close()
                            loggerRun.warn('client connect')
                            conn.setblocking(0)
                            self.conn = conn
                            break
                        else:
                            time.sleep(0.2)
                            continue

                try:
                    with self.lock:
                        data = self.queue.get(timeout=1)
                except queue.Empty:
                    print('empty')
                    continue

                self.conn.sendall(data)
                super(NetT, self).put(data)

            except socket.error as e:
                self.conn = None
                if e.errno == 32:
                    # raise DisconnectException
                    loggerRun.error('client disconnect')
                    continue
                if e.errno == 11:
                    # loggerRun.debug(u'资源占用')
                    time.sleep(0.2)
                    continue
                else:
                    loggerRun.error('Other socket error when send data: #{} {}'.format(
                        e.errno, e.strerror))
                    raise
            except Exception as e:
                self.conn = None
                loggerRun.error(
                    'Uncatched error when send data: {}'.format(str(e)))
                raise
        self.conn = None
        self.sock.close()

    def stop(self):
        logger.debug("stop")
        print('net stop')
        self.done = True
        if self.thread and self.thread.is_alive():
            print('join now')
            self.thread.join(timeout=3)
        with self.lock:
            if (self.sock):
                print('sock closeing')
                self.sock.close()

    def put(self, data):
        if (self.conn and not self.done):
            with self.lock:
                self.queue.put(data)

        #     logger.info(data)
        #     try:
        #         with self.lock:
        #             self.conn.sendall(data)
        #     except socket.error as e:
        #         self.conn = None
        #         if e.errno == 32:
        #             # raise DisconnectException
        #             logger.warn('client disconnect')
        #             return
        #         if e.errno == 11:
        #             logger.warn(u'资源占用')
        #             return
        #         else:
        #             logger.error('Other socket error when send data: #{} {}'.format(
        #                 e.errno, e.strerror))
        #             raise
        #     except Exception as e:
        #         self.conn = None
        #         logger.error(
        #             'Uncatched error when send data: {}'.format(str(e)))
        #         raise

        # super(NetT, self).put(data)
