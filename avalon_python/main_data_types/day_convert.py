#!/bin/usr/env python
# -*- coding: utf-8 -*-
from day_converter import number_to_weekday


def __main__():
    weekday_number = raw_input("Введите день недели: ")
    print number_to_weekday(int(weekday_number))


if __name__ == '__main__':
    __main__()
