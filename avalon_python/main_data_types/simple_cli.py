#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
retype = type(re.compile(r'RE'))
from collections import OrderedDict


class SimpleCLI():
    def __init__(self):
        self._commands = OrderedDict()
        self.on_syntax_error = lambda *args: None

    def reg_cmd(self, keys, descr="", action=lambda: None, syntax_descr=None):
        ''' регистрирует комманду
            keys - кортеж ключей в виде регулярных выражений или строк
            descr - описание комманды(для формирования хелпа)
            action - функция, которая будет вызвана при совпадении
            syntax_descr - используется для описания синтаксиса при
            использовании регвыров
        '''
        frozen_keys = frozenset(keys)
        self._commands[frozen_keys] = {
            'descr': descr,
            'action': action,
            'syntax_descr': syntax_descr,
        }

    def analyze(self, user_input):
        ''' анализирует пользовательский ввод '''
        for key_set in self._commands:
            # если перечисление ключей в виде строк
            if type(list(key_set)[0]) == retype:
                # если перечисление ключей в виде регулярных выражений
                for pattern in key_set:
                    res = re.match(pattern, user_input)
                    if res:
                        return self._commands[key_set]['action'](*res.groups())
            else:
                if user_input in key_set:
                    return self._commands[key_set]['action']()

        return self.on_syntax_error(user_input)

    def get_help(self, separator='\n'):
        ''' отдает справку по зарегистрированным коммандам '''
        descr_list = []
        for k, v in self._commands.items():
            if type(list(k)[0]) == str:
                descr_list.append((', '.join(k), v['descr']))
            else:
                descr_list.append((v['syntax_descr'], v['descr']))

        for keys, descr in descr_list:
            help = map(lambda (k, d,): '%s - %s' % (k, d), descr_list)

        return separator.join(help).expandtabs(4)
