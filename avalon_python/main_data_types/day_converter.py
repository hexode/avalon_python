#!/bin/usr/env python
# -*- coding: utf-8 -*-

'''
Напишите приложение, конвертирующее номер дня недели в его название.
Номер должен вводится пользователем.
Для хранениния пар номер-имя используйте словарь.

Стоимость - 10 баллов
'''

WEEKDAYS = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday',
}

WEEKDAYS_REVERSE = dict(zip(WEEKDAYS.values(), WEEKDAYS.keys()))


def number_to_weekday(weekday_number):
    '''
    конвертирует номер дня недели в его название
    '''
    assert 0 < weekday_number < 8
    return WEEKDAYS[weekday_number]
