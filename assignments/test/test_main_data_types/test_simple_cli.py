import unittest

from assignments.main_data_types.simple_cli import SimpleCLI


class TestSimpleCLI(unittest.TestCase):
    def test_simple_cmd(self):
        cli = SimpleCLI()
        display_help = lambda s=self: self.assertEqual(True, True, 'should execute specified function')
        cli.reg_cmd(('h', 'help',), 'display help', display_help)
        cli.analyze('h')

    def test_simple_cmd_aux_key(self):
        cli = SimpleCLI()
        display_help = lambda s=self: self.assertEqual(True, True, 'should execute specified function')
        cli.reg_cmd(('h', 'help',), 'display help', display_help)
        cli.analyze('help')

    def test_simple_cmd_aux_key_wrong(self):
        cli = SimpleCLI()
        display_help = lambda: self.assertEqual(True, False, 'should not execute specified function')
        cli.reg_cmd(('h', 'help',), 'display help', display_help)
        cli.analyze('wrong')
        self.assertEqual(True, True, 'should not execute specified function')

    def test_re_cmd_with_args(self):
        cli = SimpleCLI()

        def echo(something):
            self.assertEqual(something, 'True', 'should pass args to function')

        cli.reg_cmd((r'^echo:\s(.*)',), 'show something', echo)
        cli.analyze('echo True')

    def test_re_cmd_with_args_aux(self):
        cli = SimpleCLI()

        def echo(something, another):
            self.assertEqual(another, 'True', 'should pass args to function')

        cli.reg_cmd((r'^echo:\s(.*)', r'^aux:\s(.*)'), 'show something', echo)
        cli.analyze('aux True')

    def test_re_cmd_with_args_fail(self):
        cli = SimpleCLI()

        def echo(something, another):
            self.assertEqual(False, True, 'should not execute specified function')

        cli.reg_cmd((r'^echo\s(.*)', r'^aux\s(.*)'), 'show something', echo)
        cli.analyze('aux3 True')
        self.assertEqual(True, True, 'should not execute specified function')

    def test_get_help(self):
        cli = SimpleCLI()
        echo = lambda: None

        cli.reg_cmd((r'^echo\s(.*)', r'^aux\s(.*)'), 'show something', echo)
        cli.reg_cmd(('list', 'l'), 'list something', echo)

        cmds_help = cli.get_help()
        expected = '''^aux\s(.*), ^echo\s(.*)-show something
list, l-list something'''

        self.assertEqual(cmds_help, expected, 'should display help')

    def test_get_help_with_separator(self):
        cli = SimpleCLI()
        echo = lambda: None

        cli.reg_cmd((r'^echo\s(.*)', r'^aux\s(.*)'), 'show something', echo)
        cli.reg_cmd(('list', 'l'), 'list something', echo)

        separator = '\n\t'
        cmds_help = cli.get_help(separator)

        expanded_separator = separator.replace('\t', '    ')
        expected = expanded_separator.join([
            '^aux\s(.*), ^echo\s(.*) - show something',
            'list, l - list something'
        ])

        self.assertEqual(cmds_help, expected, 'should display help')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimpleCLI))
    return suite
