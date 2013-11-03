#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Напишите приложение для хранения распространённых математических констант,
таких как pi, e и др.
Реализуйте вывод значений с произвольной точностью по запросу пользователя.
Формат запроса:
<имя>:<точность>
имя - название константы,
точность - кол-во знаков после запятой.
Стоимость задания - 10 баллов
'''

from math import pi
from math import e
import sys
import os
import re

from simple_cli import SimpleCLI

clear = lambda: os.system(['clear', 'cls'][os.name == 'nt'])

__constants = {
    'pi': pi,
    'e': e,
    'sqrt2': 2 ** 0.5,
    'sqrt3': 3 ** 0.5,
    'sqrt5': 5 ** 0.5,
}

colors = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
}


def get_cstring(string, color):
    return "%s%s%s" % (colors[color], string, colors['ENDC'])


def get_constant_list():
    msg = 'List of available constants:\n'
    msg += '\t' + '\n\t'.join(sorted(__constants.keys())) + '\n'
    return msg.expandtabs(4)




def quit():
    print 'Exited'
    sys.exit(0)


def get_const(const_name):
    return __constants[const_name]


def display_help():
    print get_help()



cli = SimpleCLI()

cli.reg_cmd(('h', '?', 'help'), 'display help', display_help)
cli.reg_cmd(('l', 'list'), 'list available constants', display_constants)
cli.reg_cmd(('clear', 'cls'), 'clear screeen', clear)
cli.reg_cmd(('q', 'quit', 'exit'), 'exit from program', quit)
cli.reg_cmd((re.compile('(\w+):(\d+)'),), 'show constants', quit)


def __main__():
    print get_help()
    const_name = None
    prompt = "Enter constant and accuracy(<constant>[:<accuracy>]): "
    error_msg = 'Wrong output, please repeat your attempt'
    while True:
        while not (const_name):
            user_input = raw_input(prompt)
            if not user_input:
                continue

            if user_input in __commands['help']['keys']:
                print get_help()
                continue
            elif user_input in __commands['list']['keys']:
                print get_constant_list()
                continue
            elif user_input in __commands['clear']['keys']:
                clear()
                continue
            elif user_input in __commands['quit']['keys']:
                quit()

            if ':' not in user_input:
                user_input += ':'

            try:
                const_name, accuracy = user_input.split(':')
                const_name = const_name.lower()
                const_value = get_const(const_name)
            except:
                print get_cstring(error_msg, 'FAIL')
                const_name = accuracy = None

        accuracy = accuracy if accuracy else 10
        out = ("#.%sf" % accuracy).replace('#', '%') % const_value
        print get_cstring(out, 'OKBLUE')
        const_name = accuracy = None


if __name__ == '__main__':
    __main__()
