#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
sys.path.append(os.getcwd())
from simple_cli import SimpleCLI
from avalon_python.common.misc import get_cstring
from collections import OrderedDict
import re

'''Напишите приложение для формирования файла соответствия имён хостов и их IP адресов
и приложение для поиска записей в этом файле.
Формат файла:
    <адрес> <имя>
    например:
        127.0.0.1 localhost

        При запуске приложения необходимо считать файл, сформировать словарь,
        парами ключ-значение которого служат строчки этого файла,
        затем вывести словарь на консоль и предоставить пользователю возможность ввести новую пару.
        Пару следует добавить в конец файла.

        Второе приложение должно обеспечивать поиск по имени и адресу в том же файле.

        50 баллов
'''


CUR_DIR = os.path.dirname(__file__)
FILE_NAME = os.path.join(CUR_DIR, r'hosts')


def parse_hosts_file(filename=FILE_NAME):
    '''
    парсит входной файл на выходе отдает словарь с сохранением порядка
    дубликаты ip адресов будут устранены(будет браться первый ip адрес)
    '''
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return OrderedDict([record.strip().split()
                               for record in f.readlines()])
    return None


def add_resolv_record(ip, name, filename=FILE_NAME):
    ''' Добавляет физическую запись '''
    # TODO: проверки на наличие такого хоста не производится
    with open(filename, 'a') as f:
        f.write('%s\t%s\n' % (ip, name))


def remove_resolv_record(ip, filename=FILE_NAME):
    # Здесь можно пойти по пути оптимизации
    # и копировать файл во временный, а дальше перезаписать
    # построчно целевой исключая строку с искомым ip
    lines = None
    with open(filename, 'r+') as f:
        lines = f.readlines()
        f.truncate()

    with open(filename, 'w') as f:
        for line in lines:
            if line.split()[0] != ip:
                f.write(line)


def display_error(cmd):
    print '%s: command not found: %s' % (
        get_cstring('Syntax Error', 'FAIL'), cmd
    )


def quit(msg='exited'):
    print msg
    sys.exit(0)

# очистка экрана
clear = lambda: os.system(['clear', 'cls'][os.name == 'nt'])


#######
# MAIN
#######
def main():

    def help():
        ''' Выводит справку '''
        print get_cstring('Usage:', 'HEADER')
        help_lines = cli.get_help().split('\n')
        for help_line in help_lines:
            print '%-30s - %s' % tuple(help_line.split(' - '))
        print


    def get_records():
        ''' Возвращает список записей из файла '''
        return parse_hosts_file().items()

    def display_records(records):
        ''' Выполняет отображение записей '''
        for ip, hostname in records:
            ip_string = '%03.d.%03.d.%03.d.%03.d' % tuple(map(int, ip.split('.')))
            print '%s  %s' % (get_cstring(ip_string, 'WARNING'), hostname)

    def show_all_records():
        ''' Выводит все записи '''
        print get_cstring('All records:', 'HEADER')
        display_records(get_records())

    def tail(n=5):
        ''' Выводит n последних записей '''
        print get_cstring('Last %s records:' % n, 'HEADER')
        display_records(get_records()[-int(n):])

    def head(n=5):
        ''' Выводит n первых записей '''
        print get_cstring('First %s records:' % n, 'HEADER')
        display_records(get_records()[:int(n)])

    def find(phraze):
        ''' Ищет хосты содержащие строку phraze '''
        # Найдем записи, которые содержат искомую фразу
        records = [record for record in get_records() if phraze in record[1]]

        # подсветим фразу в имени хоста
        highlight = lambda s: get_cstring(s, 'STRONG')
        inject = lambda fn, sep, string: fn(sep).join(string.split(sep))
        records = [[i, inject(highlight, phraze, h)] for i, h in records]

        # отобразим записи
        display_records(records)

    def resolv(request):
        ''' Разрешает ip адрес или имя хоста '''
        check = re.compile(ip_address_re).match(request)
        ix = 0 if check else 1

        record = [rec for rec in get_records() if request == rec[ix]][0]
        if len(record):
            print record[not ix]

    cli = SimpleCLI()

    ip_address_re = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

    cli.reg_cmd((re.compile(r'add\s+(%s)\s+(\S+)' % ip_address_re),),
                'create record in file',
                add_resolv_record,
                'add <ip_addr> <name>')

    print r'remove\s+(%s)' % ip_address_re

    remove_re = (re.compile(r'remove\s+(%s)' % ip_address_re), )
    cli.reg_cmd(remove_re, 'remove resolv record by ip', remove_resolv_record, 'remove <ip_addr>')

    cli.reg_cmd(('show', 's', ), 'show records', show_all_records)

    tail_re = (re.compile(r'tail\s+(\d+)'), re.compile(r'tail'))
    cli.reg_cmd(tail_re, 'show last n records', tail, 'tail [n]')

    head_re = (re.compile(r'head\s+(\d+)'), re.compile(r'head'))
    cli.reg_cmd(head_re, 'show first n records', head, 'head [n]')

    find_re = (re.compile(r'find\s+(\S+)'), )
    cli.reg_cmd(find_re, 'find hostnames containing substring', find, 'find <substring>')

    resolv_re = (re.compile(r'resolv\s+(\S+)'), )
    cli.reg_cmd(resolv_re, 'resolv hostname or ip address', resolv, 'resolv <ip_addr>|<host_name>')


    cli.reg_cmd(('help', 'h', '?'), 'display help', help)
    cli.reg_cmd(('clear',), 'clear screen', clear)
    cli.reg_cmd(('quit', 'exit', 'q', 'x'), 'quit from REPL', quit)

    cli.on_syntax_error = display_error
    prompt = get_cstring("> ", 'OKGREEN')

    help()
    tail()

    while True:
        user_input = raw_input(prompt).strip()
        if not user_input:
            continue
        cli.analyze(user_input)


if __name__ == '__main__':
    main()
