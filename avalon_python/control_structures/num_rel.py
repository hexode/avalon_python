#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Напишите приложение, считывающее из файла последовательность чисел и находящую
связи между ними.
Виды искомых связей:
сумма,
разность,
произведение,
частное,
степень,
логарифм по основанию 2.
Выведите найденные комбинации чисел и вид зависимости.
Пример:
Исходная последовательность:
25,2357,32,5,75,2356,3
Вывод:
2356,1,sum,2357
25,3,mul,75
32,log2,5
и т.д.

Стоимость - 50 баллов
'''

from itertools import combinations
from math import log, sqrt
from operator import add, sub, mul, floordiv, pow as power
import argparse
import sys
import re


def main():
    parser = argparse.ArgumentParser(
        description='Find relation between numbers'
    )
    parser.add_argument('-f', '--filename', dest="filename",
                        help='read combinations from FILE')
    parser.add_argument("-s", "--separator", dest="separator",
                        help="separator between numbers")
    parser.add_argument("-u", "--unique", dest="unique", action="store_true",
                        help="exclude repeated numbers")

    options = parser.parse_args()

    separator = options.separator or r';|,'

    sequence = []

    filename = options.filename
    if filename:
        try:
            with open(filename, 'r') as f:
                for line in f:
                    sequence.extend(re.split(separator, line))
        except IOError as e:
            print "Error:%s:reading %s:%s" % (sys.argv[0], e.filename,
                                              e.strerror)
            sys.exit(1)

    if not len(sequence):
        user_input = raw_input('Input comma separated numerical sequence:\n> ')
        sequence = re.split(separator, user_input)

    sequence = map(int, sequence)
    if options.unique:
        sequence = set(sequence)

    binar_combinations = combinations(sequence, 2)

   # sub = lambda x: x[0] - x[1]
   # add = lambda x: x[0] + x[1]
   # mul = lambda x: x[0] * x[1]
   # div = lambda x: float(x[0]) / x[1]
   # power = lambda x: x[0] ** x[1]

    log2 = lambda x: log(x, 2)

    binar_func_list = [
        #(func, func_name, commutativity)
        (add, 'sum', True),
        (mul, 'mul', True),

        (sub, 'sub', False),
        (floordiv, 'div', False),
        (power,  'power', False)
    ]

    unar_func_list = [
        (log2, 'log2'),
        (sqrt, 'sqrt')
    ]

    def get_relation(args, fn, sequence):
        try:
            if type(args) == tuple:
                result = fn(*args)
            else:
                result = fn(args)
            return (result, result in sequence)
        except:
            return (None, False)

    binar_relations = []
    for arg_pair in binar_combinations:
        for func, func_name, is_commutative in binar_func_list:
            relation_number, has_relation = get_relation(arg_pair,
                                                         func, sequence)
            if has_relation:
                binar_relations.append(arg_pair + (func_name, relation_number))

            if not is_commutative:
                relation_number, has_relation = get_relation(arg_pair[::-1],
                                                             func, sequence)
                if has_relation:
                    binar_relations.append(arg_pair[::-1] + (func_name,
                                                             relation_number))

    unar_relations = []
    for arg in sequence:
        for func, func_name in unar_func_list:
            relation_number, has_relation = get_relation(arg, func, sequence)
            if has_relation:
                unar_relations.append((arg, func_name, relation_number))

    print 'Binary relations:'
    print '=' * 20
    print '\n'.join(map(lambda rel: '%-5d%-5d%-7s%-5d' % rel, binar_relations))
    print '\nUnary relations:'
    print '=' * 20
    print '\n'.join(map(lambda rel: '%-5d%-7s%-5d' % rel, unar_relations))

if __name__ == '__main__':
    main()
