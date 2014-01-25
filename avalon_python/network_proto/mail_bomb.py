#!/usr/bin/env python
#-*- coding: utf-8

'''
Напишите программу, предназначенную для рассылки компромата в
случае покушения на владельца
Программа должна создать создать udp сокет, на
который через определённые промежутки времени
должен приходить секретный код. Если код не получен
в течение 3 временных промежутков подряд,
программа должна отправить сообщение на определённый
адрес электронной почты. (30)

Подумайте, как можно повысить безопасность решения
путём отказа от передачи кода в открытом виде. (+20).
'''

import hmac
import socket
from time import time, sleep
from getpass import getpass
import argparse
import logging as log
import struct
import fcntl
import errno
import os
import sys

import smtplib


# SETTINGS
####################################################
# UDP settings
UDP_IP = '127.0.0.1'
UDP_PORT = 5005

# Be sincere
TO_ADDR = ['some@example.com', ]
FROM_ADDR = 'anonymous@mail.org'
MAIL_SUBJECT = 'FROM: address'

MESSAGE = 'WARNING: DO NOT USE AS A SUICIDE NOTE!!!'

# Your smtp credentials and settings
SMTP_LOGIN = 'smtp_login'
SMTP_PASSWORD = 'smtp_password'
SMTP_SERVER = 'smtp.gmail.com:587'

MINUTE = 60
HOUR = MINUTE * 60
DAY = 24 * HOUR
# Time after which email will be sent
TIMEOUT = 3 * DAY
#####################################################


UDP_DELAY_IN_SECONDS = 1


def check_msg(secret_key, msg):
    fmt = '>Q16s'
    if len(msg) != struct.calcsize(fmt):
        return (None, None)
    time_pack, digest = struct.unpack('8s16s', msg)
    calc_digest = hmac.new(secret_key, msg=time_pack)
    timestamp, = struct.unpack('<Q', time_pack)
    return calc_digest.digest() == digest, timestamp


def deadline(benchmark):
    return benchmark + TIMEOUT


def time_left(benchmark):
    remaining_time = deadline(benchmark) - int(time())
    return remaining_time if remaining_time >= 0 else 0


def time_is_up(benchmark):
    return time_left(benchmark) == 0


def format_time(timestamp):
    days, remainder = divmod(timestamp, DAY)
    hours, remainder = divmod(remainder, HOUR)
    minutes, seconds = divmod(remainder, MINUTE)
    return '%s:%s:%s:%s' % tuple(map(lambda e: str(e).zfill(2),
                                    (days, hours, minutes, seconds)))


def send_email(from_addr=FROM_ADDR, to_addr_list=TO_ADDR,
               cc_addr_list=[], subject=MAIL_SUBJECT,
               message=MESSAGE,
               login=SMTP_LOGIN, password=SMTP_PASSWORD,
               smtpserver=SMTP_SERVER):
    headers = []
    headers.append('From: %s' % from_addr)
    headers.append('To: %s' % ','.join(to_addr_list))
    headers.append('Cc: %s' % ','.join(cc_addr_list))
    headers.append('Subject: %s\n\n' % subject)

    message = '\n'.join(headers) + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems


def main():
    title = '''\
Send email after timeout.
if recieve udp message containing a timestamp and HMAC based on it
the timeout will be renewed.
'''

    parser = argparse.ArgumentParser(description=title)
    parser.add_argument('-v', '--verbose', dest='verbose', default=False,
                        action='store_true', help='show debug info')
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(message)s")

    secret_key = getpass("Input your secret key:")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    fcntl.fcntl(sock, fcntl.F_SETFL, os.O_NONBLOCK)

    benchmark = int(time())
    while not time_is_up(benchmark):
        try:
            # TODO: add feature - white list ip addresses
            msg, addr = sock.recvfrom(24)
            is_valid, timestamp = check_msg(secret_key, msg)
            if is_valid:
                benchmark = int(time())
                formatted_time_left = format_time(time_left(benchmark))
                log.info('Valid message recieve. Deadline updated: %s' % (
                    formatted_time_left
                ))
            else:
                formatted_time_left = format_time(time_left(benchmark))
                log.info('Wrong message recieve. Deadline: %s' % (
                    formatted_time_left
                ))
        except socket.error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                formatted_time_left = format_time(time_left(benchmark))
                log.info('Message will be sent after %s' % (
                    formatted_time_left
                ))
                sleep(UDP_DELAY_IN_SECONDS)
                continue
            else:
                log.info(e)
                sys.exit(1)

    send_email()

if __name__ == '__main__':
    main()
