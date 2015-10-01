#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitive_statsd` module.
"""

import unittest


# import mock


import importlib
netuitive_statsd = importlib.import_module(
    'netuitive-statsd')

import logging

logging.basicConfig()
logging.disable(logging.ERROR)


class Test_CONFIG(unittest.TestCase):

    def test_default_config(self):
        resp = netuitive_statsd.CONFIG
        self.assertEqual(resp['url'], 'https//api.app.netuitive.com/ingest')
        self.assertIsNotNone(resp['hostname'])
        self.assertEqual(resp['listen_ip'], '127.0.0.1')
        self.assertEqual(resp['listen_port'], 8125)
        self.assertEqual(resp['forward_ip'], '')
        self.assertEqual(resp['forward_port'], 8125)
        self.assertEqual(resp['forward'], False)
        self.assertEqual(resp['interval'], 60)
        self.assertEqual(resp['pid_file'], 'netuitive-stats.pid')
        self.assertEqual(resp['log_file'], 'netuitive-statsd.log')
        self.assertEqual(resp['debug'], False)


class Test_get_human_readable_size(unittest.TestCase):

    def test_1TB(self):
        a = netuitive_statsd.get_human_readable_size(1099511627776)
        self.assertEqual(a, '1 TB')

    def test_100GB(self):
        a = netuitive_statsd.get_human_readable_size(107374182400)
        self.assertEqual(a, '100 GB')

    def test_10GB(self):
        a = netuitive_statsd.get_human_readable_size(10737418240)
        self.assertEqual(a, '10 GB')

    def test_1GB(self):
        a = netuitive_statsd.get_human_readable_size(1073741824)
        self.assertEqual(a, '1 GB')

    def test_100MB(self):
        a = netuitive_statsd.get_human_readable_size(104857600)
        self.assertEqual(a, '100 MB')

    def test_10MB(self):
        a = netuitive_statsd.get_human_readable_size(10485760)
        self.assertEqual(a, '10 MB')

    def test_1MB(self):
        a = netuitive_statsd.get_human_readable_size(1048576)
        self.assertEqual(a, '1 MB')

    def test_100KB(self):
        a = netuitive_statsd.get_human_readable_size(102400)
        self.assertEqual(a, '100 KB')

    def test_10KB(self):
        a = netuitive_statsd.get_human_readable_size(10240)
        self.assertEqual(a, '10 KB')

    def test_1KB(self):
        a = netuitive_statsd.get_human_readable_size(1024)
        self.assertEqual(a, '1 KB')


class Test_regex_parse_message(unittest.TestCase):

    def test_single_counter(self):
        resp = netuitive_statsd.regex_parse_message(
            'counter:1|c')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'counter',
                             'type': 'c',
                             'rate': '',
                             'value': '1',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_counter_with_tags(self):
        resp = netuitive_statsd.regex_parse_message(
            'counter:1|c|#tag1,tag2,tag3:value3')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'counter',
                             'type': 'c',
                             'rate': '',
                             'value': '1',
                             'tags': [{'tag1': None}, {'tag2': None}, {u'tag3': u'value3'}]
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_counter_with_rate(self):
        resp = netuitive_statsd.regex_parse_message('counterrate:1|c|@0.1')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'counterrate',
                             'type': 'c',
                             'rate': '0.1',
                             'value': '1',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_timer(self):
        resp = netuitive_statsd.regex_parse_message('timer:320|ms')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'timer',
                             'type': 'ms',
                             'rate': '',
                             'value': '320',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_gauge(self):
        resp = netuitive_statsd.regex_parse_message('gauge:333|g')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'gauge',
                             'type': 'g',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_histogram(self):
        resp = netuitive_statsd.regex_parse_message('histogram:333|h')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'histogram',
                             'type': 'h',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_meter(self):
        resp = netuitive_statsd.regex_parse_message('meter:333|m')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'meter',
                             'type': 'm',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_set(self):
        resp = netuitive_statsd.regex_parse_message('set:333|s')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'set',
                             'type': 's',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_mutliple_metrics(self):
        self.maxDiff = None
        resp = netuitive_statsd.regex_parse_message(
            'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\nmeter:333|m|#tag1,tag2,tag3:value3\nset:333|s')

        self.assertEqual(resp,
                         {'metrics': [
                             {'metric': 'counter',
                              'type': 'c',
                              'rate': '',
                              'value': '1',
                              'tags': []
                              },
                             {'metric': 'counterrate',
                              'type': 'c',
                              'rate': '0.1',
                              'value': '1',
                              'tags': []
                              },
                             {'metric': 'timer',
                              'type': 'ms',
                              'rate': '',
                              'value': '320',
                              'tags': []
                              },
                             {'metric': 'gauge',
                              'type': 'g',
                              'rate': '',
                              'value': '333',
                              'tags': []
                              },
                             {'metric': 'histogram',
                              'type': 'h',
                              'rate': '',
                              'value': '333',
                              'tags': []
                              },
                             {'metric': 'meter',
                              'type': 'm',
                              'rate': '',
                              'value': '333',
                              'tags': [{'tag1': None}, {'tag2': None}, {u'tag3': u'value3'}]
                              },
                             {'metric': 'set',
                              'type': 's',
                              'rate': '',
                              'value': '333',
                              'tags': []}
                         ],
                             'counts':
                             {'messages': 7,
                              'events': 0},
                             'events': []
                         })

    def test_single_event(self):
        resp = netuitive_statsd.regex_parse_message(
            '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3')

        self.assertEqual(resp,
                         {'metrics': [],
                          'counts': {
                             'messages': 1,
                             'events': 1},
                          'events': [
                             {'priority': 'priority',
                              'date_happened': 'date_happened',
                              'alert_type': 'alert_type',
                              'aggregation_key': '',
                              'title': 'title',
                              'source_type_name': 'source_type_name',
                              'text': 'text',
                              'hostname': 'hostname',
                              'tags': [
                                      {'tag1': None},
                                      {'tag2': None},
                                      {'tag3': 'value3'}
                              ]}]})

    def test_badformat(self):
        badformat = netuitive_statsd.regex_parse_message('format fail|sk')
        self.assertEqual(badformat, None)


class Test_parse_message(unittest.TestCase):

    def test_single_counter(self):
        resp = netuitive_statsd.parse_message(
            'counter:1|c')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'counter',
                             'type': 'c',
                             'rate': '',
                             'value': '1',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_counter_with_tags(self):
        resp = netuitive_statsd.parse_message(
            'counter:1|c|#tag1,tag2,tag3:value3')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'counter',
                             'type': 'c',
                             'rate': '',
                             'value': '1',
                             'tags': [{'tag1': None}, {'tag2': None}, {u'tag3': u'value3'}]
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_counter_with_rate(self):
        resp = netuitive_statsd.parse_message('counterrate:1|c|@0.1')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'counterrate',
                             'type': 'c',
                             'rate': '0.1',
                             'value': '1',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_timer(self):
        resp = netuitive_statsd.parse_message('timer:320|ms')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'timer',
                             'type': 'ms',
                             'rate': '',
                             'value': '320',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_gauge(self):
        resp = netuitive_statsd.parse_message('gauge:333|g')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'gauge',
                             'type': 'g',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_histogram(self):
        resp = netuitive_statsd.parse_message('histogram:333|h')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'histogram',
                             'type': 'h',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_meter(self):
        resp = netuitive_statsd.parse_message('meter:333|m')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'meter',
                             'type': 'm',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_set(self):
        resp = netuitive_statsd.parse_message('set:333|s')
        self.assertEqual(resp,
                         {'metrics': [{
                             'metric': 'set',
                             'type': 's',
                             'rate': '',
                             'value': '333',
                             'tags': []
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_mutliple_metrics(self):
        resp = netuitive_statsd.parse_message(
            'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\nmeter:333|m|#tag1,tag2,tag3:value3\nset:333|s')

        self.assertEqual(resp,
                         {'metrics': [
                             {'metric': 'counter',
                              'type': 'c',
                              'rate': '',
                              'value': '1',
                              'tags': []
                              },
                             {'metric': 'counterrate',
                              'type': 'c',
                              'rate': '0.1',
                              'value': '1',
                              'tags': []
                              },
                             {'metric': 'timer',
                              'type': 'ms',
                              'rate': '',
                              'value': '320',
                              'tags': []
                              },
                             {'metric': 'gauge',
                              'type': 'g',
                              'rate': '',
                              'value': '333',
                              'tags': []
                              },
                             {'metric': 'histogram',
                              'type': 'h',
                              'rate': '',
                              'value': '333',
                              'tags': []
                              },
                             {'metric': 'meter',
                              'type': 'm',
                              'rate': '',
                              'value': '333',
                              'tags': [{'tag1': None}, {'tag2': None}, {u'tag3': u'value3'}]
                              },
                             {'metric': 'set',
                              'type': 's',
                              'rate': '',
                              'value': '333',
                              'tags': []}
                         ],
                             'counts':
                             {'messages': 7,
                              'events': 0},
                             'events': []
                         })

    def test_single_event(self):
        resp = netuitive_statsd.parse_message(
            '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3')

        self.assertEqual(resp,
                         {'metrics': [],
                          'counts': {
                             'messages': 1,
                             'events': 1},
                          'events': [
                             {'priority': 'priority',
                              'date_happened': 'date_happened',
                              'alert_type': 'alert_type',
                              'aggregation_key': '',
                              'title': 'title',
                              'source_type_name': 'source_type_name',
                              'text': 'text',
                              'hostname': 'hostname',
                              'tags': [
                                      {'tag1': None},
                                      {'tag2': None},
                                      {'tag3': 'value3'}
                              ]}]})

    def test_badformat(self):
        badformat = netuitive_statsd.parse_message('format fail|sk')
        self.assertEqual(badformat, None)


class Test_get_sys_meta(unittest.TestCase):

    def test_get_sys_meta(self):
        L = netuitive_statsd.get_sys_meta()
        resp = {k: v for d in L for k, v in d.items()}

        self.assertIsNotNone(resp['platform'])
        self.assertIsNotNone(resp['cpus'])
        self.assertIsNotNone(resp['ram'])
        self.assertIsNotNone(resp['ram bytes'])
        self.assertIsNotNone(resp['boottime'])
        self.assertEqual(
            resp['netuitive-statsd'], netuitive_statsd.__version__)


if __name__ == '__main__':
    unittest.main()
