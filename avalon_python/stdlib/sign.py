#!/usr/bin/python -u
#-*- coding: utf-8 -*-
'''
Напишите программу, для проверки подлинности файлов.

Предусмотрите два режима работы:

    1. Подписывание файла

    sign.py file

    Программа запрашивает пароль и генерирует хэш-код аутентификации (hmac),
    который затем дописывает в файл в кодировке Base64.

    2. Проверка подписи

    sign.py -c file


    Программа считывает код аутентификации из последней строчки файла,
    раскодирует его, запрашивает пароль, генерирует хэш-код аутентификации
    файла (без последней строчки), сравнивает хэши, выводит результат.
'''

import hmac
import hashlib
import binascii
from getpass import getpass
from collections import deque
import sys
import argparse
import logging as log


def tail_split(iterable, tail_len):
    head_len = len(iterable) - tail_len
    head, tail = iterable[:head_len], iterable[head_len:]
    return head, tail


def read_blocks(source, block_size):
    ''' read file by blocks '''
    while True:
        block = source.read(block_size)
        if not block:
            break
        yield block


class Digestify(object):
    hmac_base64_length = (
        #(alg, len)
        ('sha512', 89),
        ('sha384', 65),
        ('sha256', 45),
        ('sha224', 41),
        ('sha1', 29),
        ('md5', 25),
    )

    @staticmethod
    def sign(secret_shared_key, source=sys.stdin, target=sys.stdout,
             digestmod=hashlib.sha1, block_size=1024):
        ''' sign file by hmac '''

        digest_maker = hmac.new(key=secret_shared_key, digestmod=digestmod)

        for block in read_blocks(source, block_size):
            target.write(block)
            digest_maker.update(block)

        # write hmac in base64 to end of target
        hmac_base64 = binascii.b2a_base64(digest_maker.digest())
        log.info('HMAC: ' + hmac_base64)
        target.write(hmac_base64)

    @staticmethod
    def get_hmac_base64_length(hash_func):
        for hash_alg, hash_based64_len in Digestify.hmac_base64_length:
            if getattr(hashlib, hash_alg) == hash_func:
                return hash_based64_len

    @staticmethod
    def verify(secret_shared_key, source=sys.stdin, digestmod=hashlib.sha1,
               block_size=1024):
        ''' verify file digest '''
        hash_based64_len = Digestify.get_hmac_base64_length(digestmod)

        # for algoritm simplicity
        if block_size < hash_based64_len:
            log.error('Block size must be greater than length of HMAC(Base64)')

        digest_maker = hmac.new(key=secret_shared_key, digestmod=digestmod)

        block_deque = deque(maxlen=3)
        for block in read_blocks(source, block_size):
            block_deque.append(block)

            if len(block_deque) == 3:
                prev_block, middle_block, last_block = block_deque
                digest_maker.update(prev_block)

        # update was made
        if len(block_deque) == 3:
            _, middle_block, last_block = block_deque
            rest_block = ''.join((middle_block, last_block))

            head, hmac_base64 = tail_split(rest_block, hash_based64_len)
            digest_maker.update(head)

        # update has not been made
        elif len(block_deque) in (1, 2):
            rest_block = ''.join(block_deque)
            head, hmac_base64 = tail_split(rest_block, hash_based64_len)
            digest_maker.update(head)
        else:
            log.error('Unhandled Error')

        calc_HMAC = binascii.b2a_base64(digest_maker.digest())
        log.info("HMAC: %s" % hmac_base64)
        log.info("calculated HMAC: %s" % calc_HMAC)

        return calc_HMAC == hmac_base64


def main():
    title = 'Sign and verify HMAC for files. Stdin, stdout also supported.'
    parser = argparse.ArgumentParser(description=title)

    parser.add_argument('-s', '--source', dest='source', default=None,
                        help='source file')
    parser.add_argument('-t', '--target', dest='target', default=None,
                        help='target file')
    parser.add_argument('-c', '--verify', dest='verify', default=False,
                        action='store_true', help='verify file digest')
    parser.add_argument('--digestmod', choices=hashlib.algorithms,
                        dest='digestmod', default='sha1',
                        help='hash function for HMAC')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False,
                        action='store_true', help='show debug info')
    args = parser.parse_args()

    options = args.__dict__

    (verbose, verify, source, target, digestmod) = (
        options['verbose'],
        options['verify'],
        options['source'],
        options['target'],
        options['digestmod'],
    )

    if verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    if source:
        source = open(source, 'rb')
    if target:
        target = open(target, 'wb')

    kwargs = {
        'source': source,
        'target': target,
        'digestmod': getattr(hashlib, digestmod)
    }
    kwargs = dict(filter(lambda kv: kv[1], kwargs.items()))

    secret_shared_key = getpass("Input your secret shared key:")
    if verify:
        print u"Digest integrity check... ",
        log.info('Hash algoritm: %s' % digestmod or 'sha1')
        verify_result = Digestify.verify(secret_shared_key, **kwargs)
        if verify_result is True:
            print " Success"
            sys.exit(0)
        elif verify_result is False:
            print " Fail(Incorrect or missing digest)"
            sys.exit(1)
        elif verify_result is None:
            print " Fail(Digest is missing)"
            sys.exit(2)
    else:
        log.info('Hash algoritm: %s' % digestmod or 'sha1')
        Digestify.sign(secret_shared_key, **kwargs)
        sys.exit(0)


if __name__ == '__main__':
    main()
