import unittest

from assignments.main_data_types.day_converter import number_to_weekday


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
        for number, day in enumerate(weekdays, 1):
            result = number_to_weekday(number)
            self.assertEqual(result, day, 'Test day %s' % day)

    @unittest.expectedFailure
    def test_fail_low_limit(self):
        self.assertEqual(number_to_weekday(0), 0, 'Out of boundaries test')

    @unittest.expectedFailure
    def test_fail_high_limit(self):
        self.assertEqual(number_to_weekday(8), 0, 'Out of boundaries test')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDayConverter))
    return suite
