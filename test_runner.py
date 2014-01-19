#!/usr/bin/python
#-*- encoding: utf-8 -*-

import sys
from subprocess import call


arg_list = [
    '--nocapture',
    '--verbosity=2',
    '--with-cov',
    '--cov-report',
    'term-missing',
    '--cov',
    'avalon_python',
]

if len(sys.argv) > 1:
    cmd = sys.argv[1]
else:
    cmd = None


def show_help():
    print 'usage:'
    print './test_runner.py - run tests once'
    print './test_runner.py watch - watch directory and run test if any file changes'
    print './test_runner.py help - show this help'


if cmd == 'watch':
    call(['./bin/gorun.py', './gorun_settings.py'])
elif cmd == 'help':
    show_help()
elif len(sys.argv) == 1:
    call(['clear'])
    argv = ['./bin/nosetests']
    argv.extend(arg_list)
    call(argv)
else:
    show_help()
