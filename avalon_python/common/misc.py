#!/usr/bin/python
#-*-encoding: utf-8 -*-

colors = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
}


def get_cstring(string, color):
    ''' окрашивает строку в заданный цвет '''
    return '%s%s%s' % (colors[color], string, colors['ENDC'])
