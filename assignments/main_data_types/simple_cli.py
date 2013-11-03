#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


class SimpleCLI():
    def __init__(self):
        self.__commands = {}

    def nop(self):
        pass

    def reg_cmd(self, keys, descr="", action=nop):
        frozen_keys = frozenset(keys)
        self.__commands[frozen_keys] = {
            'descr': descr,
            'action': action,
        }


    def analyze(self, user_input):
        for key_set in self.__commands:
            # если перечисление ключей в виде строк
            if user_input in key_set:
                return self.__commands[key_set]['action']()

            # если перечисление ключей в виде регулярных выражений
            for pattern in key_set:
                res = re.match(pattern, user_input)
                if res:
                    return self.__commands[key_set]['action'](*res.groups())
        return None

    def get_help(self, separator='\n'):
        descr_list = [(k, v['descr']) for k, v in self.__commands.items()]
        msg = map(lambda (k, d,): '%s - %s' % (', '.join(k), d), descr_list)
        return separator.join(msg).expandtabs(4)



def __main__():
    cli = SimpleCLI()
    echo = lambda: None

    cli.reg_cmd((r'^echo\s(.*)', r'^aux\s(.*)'), 'show something', echo)
    cli.reg_cmd(('list', 'l'), 'list something', echo)

    cmds_help = cli.get_help()
    print cmds_help


if __name__ == '__main__':
    __main__()
