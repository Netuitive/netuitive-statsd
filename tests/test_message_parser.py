#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitivestatsd` module.
"""

import unittest
import logging

import libs

logging.basicConfig()
logging.disable(logging.ERROR)
logger = logging.getLogger(__name__)


class Test_Message_Parser(unittest.TestCase):
    maxDiff = None

    def test_bad_format(self):
        resp1 = libs.statsd.parse_message('format.fail|sk')
        resp2 = libs.statsd.parse_message('format.fail')
        resp3 = libs.statsd.parse_message('|sk')
        resp4 = libs.statsd.parse_message('format.fail| c')
        resp5 = libs.statsd.parse_message('format.fail|#tag:1')
        resp6 = libs.statsd.parse_message('format.fail||c')
        resp7 = libs.statsd.parse_message(
            'ev-api.gauge.response.swagger-resources.configuration.ui:')

        self.assertEqual(resp1, None)
        self.assertEqual(resp2, None)
        self.assertEqual(resp3, None)
        self.assertEqual(resp4, None)
        self.assertEqual(resp5, None)
        self.assertEqual(resp6, None)
        self.assertEqual(resp7, None)

    def test_sanitize_metric(self):
        resp1 = libs.statsd.parse_message('counter test:1|c')
        resp2 = libs.statsd.parse_message('counter/test:1|c')
        resp3 = libs.statsd.parse_message('counter*test:1|c')
        resp4 = libs.statsd.parse_message('counter/* test:1|c')

        self.assertEqual(resp1,
                         {'metrics': [{
                             'name': 'counter_test',
                             'type': 'c',
                             'rate': None,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

        self.assertEqual(resp2,
                         {'metrics': [{
                             'name': 'counter_test',
                             'type': 'c',
                             'rate': None,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

        self.assertEqual(resp3,
                         {'metrics': [{
                             'name': 'countertest',
                             'type': 'c',
                             'rate': None,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

        self.assertEqual(resp4,
                         {'metrics': [{
                             'name': 'counter__test',
                             'type': 'c',
                             'rate': None,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_counter(self):
        resp = libs.statsd.parse_message(
            'counter:1|c')

        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'counter',
                             'type': 'c',
                             'rate': None,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_none_response(self):
        resp = libs.statsd.parse_message(
            '')
        self.assertEqual(resp,
                         None)

    def test_single_counter_with_tags(self):
        resp = libs.statsd.parse_message(
            'counter:1|c|#tag1,tag2,tag3:value3')
        self.assertEqual(resp,
                         {'counts': {'events': 0, 'messages': 1},
                          'events': [],
                          'metrics': [{'hostname': None,
                                       'name': 'counter',
                                       'rate': None,
                                       'sign': None,
                                       'tags': [{'statsdType': 'c'},
                                                {'tag1': None},
                                                {'tag2': None},
                                                {'tag3': 'value3'}],
                                       'type': 'c',
                                       'value': 1.0}]})

    def test_single_counter_with_tags2(self):
        resp = libs.statsd.parse_message(
            'counter:1|c|#tag1,tag2,tag3:value3|#tag1,tag2,tag3:value3')
        self.assertEqual(resp,
                         {'counts': {'events': 0, 'messages': 1},
                          'events': [],
                          'metrics': [{'hostname': None,
                                       'name': 'counter',
                                       'rate': None,
                                       'sign': None,
                                       'tags': [{'statsdType': 'c'},
                                                {'tag1': None},
                                                {'tag2': None},
                                                {'tag3': 'value3'},
                                                {'tag1': None},
                                                {'tag2': None},
                                                {'tag3': 'value3'}],
                                       'type': 'c',
                                       'value': 1.0}]})

    def test_single_counter_with_tags_hostname(self):
        resp = libs.statsd.parse_message(
            'counter:1|c|#tag1,tag2,h:hostname')

        self.assertEqual(resp,
                         {'counts': {'events': 0, 'messages': 1},
                          'events': [],
                          'metrics': [{'hostname': 'hostname',
                                       'name': 'counter',
                                       'rate': None,
                                       'sign': None,
                                       'tags': [{'statsdType': 'c'},
                                                {'tag1': None},
                                                {'tag2': None},
                                                {'h': 'hostname'}],
                                       'type': 'c',
                                       'value': 1.0}]})

    def test_single_counter_with_rate(self):
        resp = libs.statsd.parse_message('counterrate:1|c|@0.1')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'counterrate',
                             'type': 'c',
                             'rate': 0.1,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_timer(self):
        resp = libs.statsd.parse_message('timer:320|ms')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'timer',
                             'type': 'ms',
                             'rate': None,
                             'sign': None,
                             'value': 320.0,
                             'tags': [{'statsdType': 'ms'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_gauge(self):
        resp = libs.statsd.parse_message('gauge:333|g')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'gauge',
                             'type': 'g',
                             'rate': None,
                             'sign': None,
                             'value': 333.0,
                             'tags': [{'statsdType': 'g'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_histogram(self):
        resp = libs.statsd.parse_message('histogram:333|h')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'histogram',
                             'type': 'h',
                             'rate': None,
                             'sign': None,
                             'value': 333.0,
                             'tags': [{'statsdType': 'h'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_set(self):
        resp = libs.statsd.parse_message('set:333|s')

        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'set',
                             'type': 's',
                             'rate': None,
                             'sign': None,
                             'value': 333.0,
                             'tags': [{'statsdType': 's'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_mutliple_metrics(self):
        resp = libs.statsd.parse_message(
            'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\ncounter.tag:333|c|#tag1,tag2,tag3:value3,h:testhost2\nset:333|s')

        self.assertEqual(resp,
                         {'counts': {'events': 0, 'messages': 7},
                          'events': [],
                             'metrics': [{'hostname': None,
                                          'name': 'counter',
                                          'rate': None,
                                          'sign': None,
                                          'tags': [{'statsdType': 'c'}],
                                          'type': 'c',
                                          'value': 1.0},
                                         {'hostname': None,
                                          'name': 'counterrate',
                                          'rate': 0.1,
                                          'sign': None,
                                          'tags': [{'statsdType': 'c'}],
                                          'type': 'c',
                                          'value': 1.0},
                                         {'hostname': None,
                                          'name': 'timer',
                                          'rate': None,
                                          'sign': None,
                                          'tags': [{'statsdType': 'ms'}],
                                          'type': 'ms',
                                          'value': 320.0},
                                         {'hostname': None,
                                          'name': 'gauge',
                                          'rate': None,
                                          'sign': None,
                                          'tags': [{'statsdType': 'g'}],
                                          'type': 'g',
                                          'value': 333.0},
                                         {'hostname': None,
                                          'name': 'histogram',
                                          'rate': None,
                                          'sign': None,
                                          'tags': [{'statsdType': 'h'}],
                                          'type': 'h',
                                          'value': 333.0},
                                         {'hostname': 'testhost2',
                                          'name': 'counter.tag',
                                          'rate': None,
                                          'sign': None,
                                          'tags': [{'statsdType': 'c'},
                                                   {'tag1': None},
                                                   {'tag2': None},
                                                   {'tag3': 'value3'},
                                                   {'h': 'testhost2'}],
                                          'type': 'c',
                                          'value': 333.0},
                                         {'hostname': None,
                                          'name': 'set',
                                          'rate': None,
                                          'sign': None,
                                          'tags': [{'statsdType': 's'}],
                                          'type': 's',
                                          'value': 333.0}]})

    def test_single_event(self):
        resp = libs.statsd.parse_message(
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
                              'aggregation_key': 'aggregation_key',
                              'title': 'title',
                              'source_type_name': 'source_type_name',
                              'text': 'text',
                              'hostname': 'hostname',
                              'tags': [
                                      {'tag1': None},
                                      {'tag2': None},
                                      {'tag3': 'value3'}
                              ]}]})

    def test_single_service_check(self):
        resp = libs.statsd.parse_message(
            '_sc|check.name|0|d:timestamp|h:hostname|#tag1,tag2,tag3:value3|m:message')

        self.assertEqual(resp,
                         {'counts': {'events': 1, 'messages': 1},
                          'events': [{'aggregation_key': None,
                                      'alert_type': None,
                                      'date_happened': 'timestamp',
                                      'hostname': 'hostname',
                                      'priority': 'OK',
                                      'source_type_name': None,
                                      'tags': [{'tag1': None}, {'tag2': None}, {'tag3': 'value3'}],
                                      'text': 'message',
                                      'title': 'check.name - OK'}],
                             'metrics': []})

    def test_metric_startswith_dot(self):
        resp = libs.statsd.parse_message(
            '.counter:1|c')

        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'counter',
                             'type': 'c',
                             'rate': None,
                             'sign': None,
                             'value': 1.0,
                             'tags': [{'statsdType': 'c'}],
                             'hostname': None
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })


if __name__ == '__main__':
    unittest.main()
