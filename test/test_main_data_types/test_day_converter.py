#!-*- encoding: utf-8 -*-
import unittest

from avalon_python.main_data_types.day_converter import number_to_weekday


weekdays = (
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
)


class TestDayConverter(unittest.TestCase):
    def test_days(self):
        ''' number_to_weekday должен корректно преобразовать
        числа в день недели '''
        for number, day in enumerate(weekdays, 1):
            result = number_to_weekday(number)
            self.assertEqual(result, day, 'Test day %s' % day)

    @unittest.expectedFailure
    def test_fail_low_limit(self):
        ''' должен падать при выходе за границы (кейс 1) '''
        self.assertEqual(number_to_weekday(0), 0, 'Out of boundaries test')

    @unittest.expectedFailure
    def test_fail_high_limit(self):
        ''' должен падать при выходе за границы (кейс 2)'''
        self.assertEqual(number_to_weekday(8), 0, 'Out of boundaries test')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDayConverter))
    return suite
