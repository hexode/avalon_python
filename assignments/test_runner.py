#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import nose

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

# import unittest
# from assignments.main_data_types import test_day_converter


def __main__():
    result = nose.run()
    # suite = unittest.TestSuite()
    # suite.addTest(test_day_converter.suite())

    # unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    __main__()
