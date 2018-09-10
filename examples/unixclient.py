# -*- coding: utf-8 -*-
import socket
import os

print("Connecting...")
if os.path.exists("/tmp/echo1.sock"):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect("/tmp/echo1.sock")
    print("Ready.")
    print("Ctrl-C to quit.")
    print("Sending 'DONE' shuts down the server and quits.")
    while True:
        try:
            data = client.recv(128)
            print data
        except KeyboardInterrupt as k:
            print("Shutting down.")
            client.close()
            break
else:
    print("Couldn't Connect!")
