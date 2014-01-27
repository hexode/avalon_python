#!/usr/bin/env python
#-*- coding: utf-8
import hmac
import socket
from time import time
from getpass import getpass
import struct

# Settings
UDP_IP = '127.0.0.1'
UDP_PORT = 9876


def generate_msg(secret_key):
    timestamp = int(time())
    time_pack = struct.pack('<Q', timestamp)
    digest = hmac.new(secret_key, msg=time_pack).digest()
    msg = time_pack + digest
    return msg


def main():
    secret_key = getpass("Input your secret key:")
    try:
        msg = generate_msg(secret_key)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg, (UDP_IP, UDP_PORT))
        print 'Message sent'
    except:
        print 'Something wrong occurs'

if __name__ == '__main__':
    main()
