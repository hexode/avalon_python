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
import errno
import sys

import smtplib


# SETTINGS
####################################################
# UDP settings
UDP_IP = '0.0.0.0'
UDP_PORT = 9876

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


def deadline(timestamp):
    return timestamp + TIMEOUT


def time_left(timestamp):
    remaining_time = deadline(timestamp) - int(time())
    return remaining_time if remaining_time >= 0 else 0


def time_is_up(timestamp):
    return time_left(timestamp) == 0


def format_time(timestamp):
    days, remainder = divmod(timestamp, DAY)
    hours, remainder = divmod(remainder, HOUR)
    minutes, seconds = divmod(remainder, MINUTE)
    return '%02dd:%02dh:%02dm:%02ds' % (days, hours, minutes, seconds)


def send_email(from_addr=FROM_ADDR, to_addr_list=TO_ADDR,
               cc_addr_list=(), subject=MAIL_SUBJECT,
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
    sock.settimeout(1.0)
    sock.setblocking(0)

    timestamp = int(time())
    while not time_is_up(timestamp):
        try:
            msg, addr = sock.recvfrom(512)
            is_valid, timestamp = check_msg(secret_key, msg)
            if is_valid:
                timestamp = int(time())
                formatted_time_left = format_time(time_left(timestamp))
                log.info('Valid message recieve. Deadline updated: %s',
                         formatted_time_left)
            else:
                formatted_time_left = format_time(time_left(timestamp))
                log.info('Wrong message recieve. Deadline: %s',
                         formatted_time_left)
        except socket.timeout, e:
            err = e.args[0]
            if err == 'timed out':
                continue
        except socket.error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                log.info('Deadline: %s', format_time(time_left(timestamp)))
                sleep(1)
                continue

            log.error(e)
            sys.exit(1)

    send_email()

if __name__ == '__main__':
    main()
