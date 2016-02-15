#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitivestatsd` module.
"""

import unittest
import os
import json
import importlib
import logging
import threading
import netuitivestatsd

import importlib
netuitive_statsd = importlib.import_module(
    'netuitive-statsd')

try:
    from cStringIO import StringIO

except ImportError:
    try:
        from StringIO import StringIO

    except ImportError:
        from io import StringIO

logging.basicConfig()
logging.disable(logging.ERROR)


def getFixtureDirPath():
    path = os.path.join(
        os.path.dirname('tests/'),
        'fixtures')
    return path


def getFixturePath(fixture_name):
    path = os.path.join(getFixtureDirPath(),
                        fixture_name)
    if not os.access(path, os.R_OK):
        print('Missing Fixture ' + path)
    return path


def getFixture(fixture_name):
    with open(getFixturePath(fixture_name), 'r') as f:
        return StringIO(f.read())


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


class Test_parse_message(unittest.TestCase):
    # maxDiff = None

    def test_bad_format(self):
        badformat = netuitivestatsd.statsd.parse_message('format fail|sk')
        self.assertEqual(badformat, None)

    def test_single_counter(self):
        resp = netuitivestatsd.statsd.parse_message(
            'counter:1|c')

        self.assertDictEqual(resp,
                             {'metrics': [{
                                 'name': 'counter',
                                 'type': 'c',
                                 'rate': None,
                                 'sign': None,
                                 'value': 1.0,
                                 'tags': [{'statsdType': 'c'}]
                             }],
                                 'counts': {
                                 'messages': 1,
                                 'events': 0
                             },
                                 'events': []
                             })

    def test_single_counter_with_tags(self):
        resp = netuitivestatsd.statsd.parse_message(
            'counter:1|c|#tag1,tag2,tag3:value3')
        self.assertDictEqual(resp,
                             {'metrics': [{
                                 'name': 'counter',
                                 'type': 'c',
                                 'rate': None,
                                 'sign': None,
                                 'value': 1.0,
                                 'tags': [{'statsdType': 'c'}, {'tag1': None}, {'tag2': None}, {'tag3': 'value3'}]
                             }],
                                 'counts': {
                                 'messages': 1,
                                 'events': 0
                             },
                                 'events': []
                             })

    def test_single_counter_with_rate(self):
        resp = netuitivestatsd.statsd.parse_message('counterrate:1|c|@0.1')
        self.assertDictEqual(resp,
                             {'metrics': [{
                                 'name': 'counterrate',
                                 'type': 'c',
                                 'rate': 0.1,
                                 'sign': None,
                                 'value': 1.0,
                                 'tags': [{'statsdType': 'c'}]
                             }],
                                 'counts': {
                                 'messages': 1,
                                 'events': 0
                             },
                                 'events': []
                             })

    def test_single_timer(self):
        resp = netuitivestatsd.statsd.parse_message('timer:320|ms')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'timer',
                             'type': 'ms',
                             'rate': None,
                             'sign': None,
                             'value': 320.0,
                             'tags': [{'statsdType': 'ms'}]
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_gauge(self):
        resp = netuitivestatsd.statsd.parse_message('gauge:333|g')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'gauge',
                             'type': 'g',
                             'rate': None,
                             'sign': None,
                             'value': 333.0,
                             'tags': [{'statsdType': 'g'}]
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_histogram(self):
        resp = netuitivestatsd.statsd.parse_message('histogram:333|h')
        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'histogram',
                             'type': 'h',
                             'rate': None,
                             'sign': None,
                             'value': 333.0,
                             'tags': [{'statsdType': 'h'}]
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_single_set(self):
        resp = netuitivestatsd.statsd.parse_message('set:333|s')

        self.assertEqual(resp,
                         {'metrics': [{
                             'name': 'set',
                             'type': 's',
                             'rate': None,
                             'sign': None,
                             'value': 333.0,
                             'tags': [{'statsdType': 's'}]
                         }],
                             'counts': {
                             'messages': 1,
                                 'events': 0
                         },
                             'events': []
                         })

    def test_mutliple_metrics(self):
        resp = netuitivestatsd.statsd.parse_message(
            'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\ncounter.tag:333|c|#tag1,tag2,tag3:value3\nset:333|s')

        self.assertEqual(resp,
                         {'metrics': [
                             {'name': 'counter',
                              'type': 'c',
                              'rate': None,
                              'sign': None,
                              'value': 1.0,
                              'tags': [{'statsdType': 'c'}]
                              },
                             {'name': 'counterrate',
                              'type': 'c',
                              'rate': 0.1,
                              'sign': None,
                              'value': 1.0,
                              'tags': [{'statsdType': 'c'}]
                              },
                             {'name': 'timer',
                              'type': 'ms',
                              'rate': None,
                              'sign': None,
                              'value': 320.0,
                              'tags': [{'statsdType': 'ms'}]
                              },
                             {'name': 'gauge',
                              'type': 'g',
                              'rate': None,
                              'sign': None,
                              'value': 333.0,
                              'tags': [{'statsdType': 'g'}]
                              },
                             {'name': 'histogram',
                              'type': 'h',
                              'rate': None,
                              'sign': None,
                              'value': 333.0,
                              'tags': [{'statsdType': 'h'}]
                              },
                             {'name': 'counter.tag',
                              'type': 'c',
                              'rate': None,
                              'sign': None,
                              'value': 333.0,
                              'tags': [{'statsdType': 'c'}, {'tag1': None}, {'tag2': None}, {'tag3': 'value3'}]
                              },
                             {'name': 'set',
                              'type': 's',
                              'rate': None,
                              'sign': None,
                              'value': 333.0,
                              'tags': [{'statsdType': 's'}]}
                         ],
                             'counts':
                             {'messages': 7,
                              'events': 0},
                             'events': []
                         })

    def test_single_event(self):
        resp = netuitivestatsd.statsd.parse_message(
            '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3')

        self.assertDictEqual(resp,
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


class Test_Poster(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.CONFIG = {}
        self.CONFIG['debug'] = True

        # Defaults
        self.CONFIG['interval'] = 60
        self.CONFIG['element_type'] = "SERVER"
        self.CONFIG['prefix'] = "statsd"
        self.CONFIG['listen_port'] = 8125
        self.CONFIG['listen_ip'] = '127.0.0.1'
        self.CONFIG['forward_port'] = None
        self.CONFIG['forward_ip'] = None
        self.CONFIG['forward'] = False
        self.CONFIG['configfile'] = 'test.cfg'
        self.CONFIG['url'] = 'http://test.com'
        self.CONFIG['api_key'] = 'testapiket'
        self.CONFIG['hostname'] = 'testelement'

        self.timestamp = 1434110794
        self.myElement = netuitive_statsd.Element(self.CONFIG['hostname'])
        self.poster = netuitive_statsd.Poster(self.CONFIG, self.myElement)
        self.poster.start()

        self.lock = threading.Lock()

    def test_single_counter(self):

        with self.lock:
            self.poster.submit('counter:1|c', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_counter').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_counter_with_tags(self):
        with self.lock:
            self.poster.submit(
                'counter:1|c|#tag1,tag2,tag3:value3', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_counter_with_tags').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_counter_with_rate(self):
        with self.lock:
            self.poster.submit(
                'counterrate:1|c|@0.1', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_counter_with_rate').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_timer(self):
        with self.lock:
            self.poster.submit(
                'timer:320|ms', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_timer').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_gauge(self):
        with self.lock:
            self.poster.submit(
                'gauge:333|g', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_gauge').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_histogram(self):
        with self.lock:
            self.poster.submit(
                'histogram:333|h', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_histogram').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_set(self):
        with self.lock:
            self.poster.submit(
                'set:333|s', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_set').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_mutliple_metrics(self):

        with self.lock:
            self.poster.submit(
                'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\ncounter.tag:333|c|#tag1,tag2,tag3:value3\nset:333|s', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

                j = json.dumps(
                    element, default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_mutliple_metrics').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(element.samples[0].timestamp))

            self.poster.elements.delete(ename)

            self.assertEqual(j, f)

    def test_single_event(self):
        with self.lock:
            self.poster.submit(
                '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3', self.timestamp)

            for event in self.poster.events:

                j = json.dumps(
                    [event], default=lambda o: o.__dict__, sort_keys=True)

                f = getFixture('Test_Poster.test_single_event').getvalue().replace(
                    'TIMESTAMP_TEMPLATE', str(event.timestamp))

            self.poster.events = []
            self.assertEqual(j, f)

    def tearDown(self):
        self.poster.stop()


if __name__ == '__main__':
    unittest.main()
