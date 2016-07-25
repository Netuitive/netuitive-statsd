#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitivestatsd` module.
"""

import unittest
import logging
import os
import socket

import libs

logging.basicConfig()
logging.disable(logging.ERROR)
# logger = logging.getLogger(__name__)


class Test_Config(unittest.TestCase):
    maxDiff = None

    def test_defaults(self):
        resp = libs.config()
        defaults = {'enabled': True,
                    'api_key': None,
                    'debug': False,
                    'element_type': 'SERVER',
                    'forward': False,
                    'forward_ip': None,
                    'forward_port': None,
                    'hostname': socket.getfqdn().split('.')[0],
                    'interval': 60,
                    'listen_ip': '127.0.0.1',
                    'listen_port': 8125,
                    'log_file': 'netuitive-statsd.log',
                    'pid_file': 'netuitive-statsd.pid',
                    'prefix': 'statsd',
                    'foreground': False,
                    'nolog': False,
                    'url': 'https://api.app.netuitive.com/ingest',
                    'no_internal_metrics': False}

        self.assertEqual(resp, defaults)

    def test_missing_configfile(self):
        args = {u'--api_key': None,
                u'--configfile': 'tests/netuitive-statsd.conf.missing',
                u'--debug': False,
                u'--element_type': u'statsd',
                u'--forward': False,
                u'--forward_ip': None,
                u'--forward_port': 8125,
                u'--hostname': None,
                u'--interval': u'60',
                u'--listen_ip': u'127.0.0.1',
                u'--listen_port': 8125,
                u'--log_file': u'./netuitive-statsd.log',
                u'--log_level': u'WARNING',
                u'--pid_file': u'./netuitive-statsd.pid',
                u'--prefix': u'statsd',
                u'--foreground': False,
                u'--nolog': False,
                u'--url': u'https://api.app.netuitive.com/ingest',
                u'<command>': 'info',
                u'--no_internal_metrics': False}

        try:
            resp = libs.config(args)

        except:
            return

        raise AssertionError('should raise an exception')

    def test_args_and_configfile(self):
        args = {u'--api_key': None,
                u'--configfile': 'tests/netuitive-statsd.conf.test',
                u'--debug': False,
                u'--element_type': u'statsd',
                u'--forward': False,
                u'--forward_ip': None,
                u'--forward_port': 8125,
                u'--hostname': None,
                u'--interval': 10,
                u'--listen_ip': u'127.0.0.1',
                u'--listen_port': 8125,
                u'--log_file': u'./netuitive-statsd.log',
                u'--log_level': u'WARNING',
                u'--pid_file': u'./netuitive-statsd.pid',
                u'--prefix': u'statsd',
                u'--foreground': False,
                u'--nolog': False,
                u'--url': u'https://api.app.netuitive.com/ingest',
                u'<command>': 'info',
                u'--no_internal_metrics': False}

        resp = libs.config(args)

        expected = {'enabled': True,
                    'api_key': '<valid api key>',
                    'configfile': os.path.abspath(args['--configfile']),
                    'debug': False,
                    'element_type': 'SERVER',
                    'forward': True,
                    'forward_ip': '127.0.0.2',
                    'forward_port': 8125,
                    'hostname': 'statsd-test-host',
                    'interval': 10,
                    'listen_ip': '127.0.0.1',
                    'listen_port': 8125,
                    'log_file': './netuitive-statsd.log',
                    'log_level': 'INFO',
                    'pid_file': './netuitive-statsd.pid',
                    'prefix': 'statsd',
                    'foreground': False,
                    'nolog': False,
                    'url': 'https://api.app.netuitive.com/ingest/infrastructure',
                    'no_internal_metrics': False}

        self.assertEqual(resp, expected)

    def test_args_only(self):
        args = {u'--api_key': '123',
                u'--configfile': None,
                u'--debug': True,
                u'--element_type': u'statsd',
                u'--forward': False,
                u'--forward_ip': None,
                u'--forward_port': 8125,
                u'--hostname': None,
                u'--interval': 60,
                u'--listen_ip': u'127.0.0.1',
                u'--listen_port': 8125,
                u'--log_file': u'./netuitive-statsd.log',
                u'--log_level': u'WARNING',
                u'--pid_file': u'./netuitive-statsd.pid',
                u'--prefix': u'statsd',
                u'--foreground': False,
                u'--nolog': False,
                u'--url': u'https://api.app.netuitive.com/ingest',
                u'<command>': 'info',
                u'--no_internal_metrics': False}

        resp = libs.config(args)

        expected = {'enabled': True,
                    'api_key': '123',
                    'configfile': None,
                    'debug': True,
                    'element_type': 'statsd',
                    'forward': False,
                    'forward_ip': None,
                    'forward_port': 8125,
                    'hostname': None,
                    'interval': 60,
                    'listen_ip': '127.0.0.1',
                    'listen_port': 8125,
                    'log_file': './netuitive-statsd.log',
                    'log_level': 'DEBUG',
                    'pid_file': './netuitive-statsd.pid',
                    'prefix': 'statsd',
                    'foreground': False,
                    'nolog': False,
                    'url': 'https://api.app.netuitive.com/ingest',
                    'no_internal_metrics': False}

        self.assertEqual(resp, expected)

if __name__ == '__main__':
    unittest.main()
