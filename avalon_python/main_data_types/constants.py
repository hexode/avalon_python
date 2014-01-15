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
sys.path.append(os.getcwd())
import re

from simple_cli import SimpleCLI
from avalon_python.common.misc import get_cstring

clear = lambda: os.system(['clear', 'cls'][os.name == 'nt'])

_constants = {
    'pi': pi,
    'e': e,
    'sqrt2': 2 ** 0.5,
    'sqrt3': 3 ** 0.5,
    'sqrt5': 5 ** 0.5,
}


def get_const(const_name):
    if const_name in _constants:
        return _constants[const_name]


def get_constant_list():
    msg = 'List of available constants:\n'
    msg += '\t' + '\n\t'.join(sorted(_constants.keys())) + '\n'
    return msg.expandtabs(4)


def quit():
    print 'Exited'
    sys.exit(0)


def display_constants():
    print get_constant_list()


def display_constant(const_name, const_accuracy=None):
    if not const_accuracy:
        const_accuracy = 5
    const_value = get_const(const_name)
    const_accuracy = int(const_accuracy)
    if const_value:
        print 'const %s = %.*f' % (get_cstring(const_name, 'HEADER'), const_accuracy, const_value)


def __main__():
    cli = SimpleCLI()

    def display_help():
        print cli.get_help()

    def display_error(cmd):
        print get_cstring('Unknow command %s' % cmd, 'FAIL')
        print get_cstring('use help to show all available commands', 'FAIL')

    cli.reg_cmd(('h', '?', 'help'), 'display help', display_help)
    cli.reg_cmd(('l', 'list'), 'list available constants', display_constants)
    cli.reg_cmd(('clear', 'cls'), 'clear screen', clear)
    cli.reg_cmd(('q', 'quit', 'exit'), 'exit from program', quit)
    constants = _constants.keys()

    syntax = re.compile(r'(%s):(\d*)' % '|'.join(constants))
    cli.reg_cmd((syntax,), 'show constants', display_constant, '<constant>:[<accuracy>]')
    cli.on_syntax_error = display_error

    print display_help()
    const_name = None
    prompt = "Enter constant and accuracy(<constant>[:<accuracy>]): "
    while True:
        while not (const_name):
            user_input = raw_input(prompt)
            if not user_input:
                continue
            cli.analyze(user_input)


if __name__ == '__main__':
    __main__()
