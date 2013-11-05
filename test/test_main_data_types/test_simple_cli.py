#!/bin/bash
#-*- encoding: utf-8 -*-
import unittest
import re
from mock import Mock

from avalon_python.main_data_types.simple_cli import SimpleCLI


class TestSimpleCLI(unittest.TestCase):
    def setUp(self):
        self.cli = SimpleCLI()

    def test_analyze_first_key(self):
        '''  analyze должен вызывать при совпадении с первым ключом команду '''

        display_help = Mock()

        self.cli.reg_cmd(('h', 'help',), 'display help', display_help)
        self.cli.analyze('h')

        self.assertTrue(display_help.call_count == 1,
                        'should execute command once if key is matched')

    def test_analyze_aux_key(self):
        '''  analyze должен вызывать при совпадении с дополнительными
        ключам команду '''

        display_help = Mock()

        self.cli.reg_cmd(('h', 'help',), 'display help', display_help)
        self.cli.analyze('help')

        self.assertTrue(display_help.call_count == 1,
                        'should execute command once if aux key is matched')

    def test_analyze_unknow_cmd(self):
        '''  analyze не должен вызывать при несовпадении с ключами команду '''

        display_help = Mock()

        self.cli.reg_cmd(('h', 'help',), 'display help', display_help)
        self.cli.analyze('wrong')

        self.assertTrue(display_help.call_count == 0,
                        'should never execute any command')

    def test_analyze_re_keys(self):
        ''' analyze должен уметь работать с регулярными выражениями '''

        echo = Mock()

        self.cli.reg_cmd((re.compile(r'^echo\s(.*)'),), 'show something', echo)
        self.cli.analyze('echo foo')

        self.assertTrue(echo.call_count == 1,
                        'should pass args to function from parsed regular expression')

    def test_analyze_re_keys_with_args(self):
        ''' analyze должен вызывать функцию с результатами
        регулярного выражения(подстроки группировок) '''

        echo = Mock()

        self.cli.reg_cmd((re.compile(r'^echo\s(.*)'),), 'show something', echo)
        self.cli.analyze('echo foo')

        self.assertTrue(echo.call_args == (('foo',),),
                       'should pass args to function from parsed regular expression')

    def test_analyze_re_aux_keys(self):
        ''' analyze должен уметь работать с регулярными
        выражениями (дополнительные ключи) '''
        echo = Mock()

        self.cli.reg_cmd((re.compile(r'^echo\s(.*)'), re.compile(r'^aux\s(.*)')),
                         'show something', echo)
        self.cli.analyze('aux foo')
        self.assertTrue(echo.call_count == 1,
                        'should work with regular expressions (auxilary keys)')

    def test_re_cmd_with_args_fail(self):
        ''' analyze не должен вызывать метод, если ключ
        не сматчился на регулярное выражение '''

        echo = Mock()
        self.cli.reg_cmd((r'^echo\s(.*)', r'^aux\s(.*)'),
                         'show something', echo)
        self.cli.analyze('aux3 foo')

        self.assertTrue(echo.call_count == 0,
                        'should not execute specified function')

    def test_get_help(self):

        echo = lambda: None

        self.cli.reg_cmd((re.compile(r'^echo\s(.*)'),
                         re.compile(r'^aux\s(.*)')), 'show something', echo, 'aux|echo <something>')
        self.cli.reg_cmd(('list', 'l'), 'list something', echo)

        cmds_help = self.cli.get_help()
        expected = '''aux|echo <something> - show something
list, l - list something'''

        self.assertEqual(cmds_help, expected, 'should display help')

    def test_get_help_with_separator(self):

        echo = lambda: None

        self.cli.reg_cmd((re.compile(r'^echo\s(.*)'),
                         re.compile(r'^aux\s(.*)')),
                         'show something', echo,  'aux|echo <something>')
        self.cli.reg_cmd(('list', 'l'), 'list something', echo)

        separator = '\n\t'
        cmds_help = self.cli.get_help(separator)

        expanded_separator = separator.replace('\t', ' ' * 4)

        expected = expanded_separator.join([
            r'aux|echo <something> - show something',
            r'list, l - list something'
        ])

        self.assertTrue(cmds_help == expected, 'should display help')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimpleCLI))
    return suite
