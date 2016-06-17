#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitivestatsd` module.
"""

import unittest
import mock
import json
import logging
import threading

import libs

logging.basicConfig()
logging.disable(logging.ERROR)
logger = logging.getLogger(__name__)


class MockResponse(object):

    def __init__(self,
                 resp_data='',
                 headers={'content-type': 'text/plain; charset=utf-8'},
                 code=200,
                 msg='OK',
                 resp_headers=None):

        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = headers
        self.resp_headers = resp_headers

    def read(self):
        return self.resp_data

    def info(self):
        return dict(self.resp_headers)

    def getcode(self):
        return self.code

    def close(self):
        return True


class Test_Poster(unittest.TestCase):
    maxDiff = None

    def setUp(self):

        self.config = {'api_key': 'testapiket',
                       'debug': True,
                       'element_type': 'SERVER',
                       'forward': False,
                       'forward_ip': None,
                       'forward_port': None,
                       'hostname': 'testelement',
                       'interval': 60,
                       'listen_ip': '127.0.0.1',
                       'configfile': 'test.cfg',
                       'listen_port': 8125,
                       'prefix': 'statsd',
                       'foreground': False,
                       'url': 'http://test.com'}

        self.config2 = {'api_key': 'testapiket',
                        'debug': True,
                        'element_type': 'NOTSERVER',
                        'forward': False,
                        'forward_ip': None,
                        'forward_port': None,
                        'hostname': 'testelement2',
                        'interval': 60,
                        'listen_ip': '127.0.0.1',
                        'configfile': 'test.cfg',
                        'listen_port': 8125,
                        'prefix': 'statsd',
                        'foreground': False,
                        'url': 'http://test.com'}

        self.timestamp = 1434110794

        self.myElement = libs.Element(
            self.config['hostname'], self.config['element_type'])
        self.poster = libs.Poster(self.config, self.myElement)
        self.poster.start()

        self.poster2 = libs.Poster(self.config, self.myElement, 8)

        self.myElement2 = libs.Element(
            self.config2['hostname'], self.config2['element_type'])
        self.poster3 = libs.Poster(self.config2, self.myElement2)
        self.poster3.start()

        self.myElement3 = libs.Element(
            self.config['hostname'], self.config['element_type'])
        self.poster4 = libs.Poster(self.config, self.myElement3)
        self.poster4.start()

        self.myElement4 = libs.Element(
            self.config['hostname'], self.config['element_type'])
        self.poster5 = libs.Poster(self.config, self.myElement4)
        self.poster5.start()

        self.lock = threading.Lock()

    def test_Poster_config(self):
        self.assertEqual(self.poster.api.agent, 'Netuitive-Statsd/develop')
        self.assertEqual(self.poster2.api.agent, 'Netuitive-Statsd/8')

    def test_single_counter(self):

        with self.lock:
            self.poster.submit('counter:1|c', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.counter',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'c'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 1.0,
                                                          'cnt': 1.0,
                                                          'max': 1.0,
                                                          'metricId': 'statsd.counter',
                                                          'min': 1.0,
                                                          'sum': 1.0,
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 1.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.counter': {'avg': None,
                                                                'cnt': 0.0,
                                                                'max': None,
                                                                'metricType': 'GAUGE',
                                                                'min': None,
                                                                'name': 'statsd.counter',
                                                                'orgtype': ['COUNTER'],
                                                                'samples': [],
                                                                'signed': False,
                                                                'sparseDataStrategy': 'None',
                                                                'sum': None,
                                                                'tags': [{'statsdType': 'c'}],
                                                                'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.counter'].timestamp,
                                                                'unit': '',
                                                                'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_single_counter_with_tags(self):
        with self.lock:
            self.poster.submit(
                'counter:1|c|#tag1,tag2,tag3:value3', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.counter',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'c'},
                                                                   {'name': 'tag1',
                                                                    'value': None},
                                                                   {'name': 'tag2',
                                                                    'value': None},
                                                                   {'name': 'tag3',
                                                                    'value': 'value3'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 1.0,
                                                          'cnt': 1.0,
                                                          'max': 1.0,
                                                          'metricId': 'statsd.counter',
                                                          'min': 1.0,
                                                          'sum': 1.0,
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 1.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.counter': {'avg': None,
                                                                'cnt': 0.0,
                                                                'max': None,
                                                                'metricType': 'GAUGE',
                                                                'min': None,
                                                                'name': 'statsd.counter',
                                                                'orgtype': ['COUNTER'],
                                                                'samples': [],
                                                                'signed': False,
                                                                'sparseDataStrategy': 'None',
                                                                'sum': None,
                                                                'tags': [{'statsdType': 'c'},
                                                                         {'tag1': None},
                                                                         {'tag2': None},
                                                                         {'tag3': 'value3'}],
                                                                'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.counter'].timestamp,
                                                                'unit': '',
                                                                'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_single_counter_with_rate(self):
        with self.lock:
            self.poster.submit(
                'counterrate:1|c|@0.1', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.counterrate',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'c'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 0.1,
                                                          'cnt': 1.0,
                                                          'max': 0.1,
                                                          'metricId': 'statsd.counterrate',
                                                          'min': 0.1,
                                                          'sum': 0.1,
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 0.1}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.counterrate': {'avg': None,
                                                                    'cnt': 0.0,
                                                                    'max': None,
                                                                    'metricType': 'GAUGE',
                                                                    'min': None,
                                                                    'name': 'statsd.counterrate',
                                                                    'orgtype': ['COUNTER'],
                                                                    'samples': [],
                                                                    'signed': False,
                                                                    'sparseDataStrategy': 'None',
                                                                    'sum': None,
                                                                    'tags': [{'statsdType': 'c'}],
                                                                    'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.counterrate'].timestamp,
                                                                    'unit': '',
                                                                    'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_single_timer(self):
        with self.lock:
            self.poster.submit(
                'timer:320|ms', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.timer',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'ms'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 320.0,
                                                          'cnt': 1.0,
                                                          'max': 320.0,
                                                          'metricId': 'statsd.timer',
                                                          'min': 320.0,
                                                          'sum': 320.0,
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 320.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.timer': {'avg': None,
                                                              'cnt': 0.0,
                                                              'max': None,
                                                              'metricType': 'GAUGE',
                                                              'min': None,
                                                              'name': 'statsd.timer',
                                                              'orgtype': ['TIMER',
                                                                          'HISTOGRAM'],
                                                              'percentile': 0,
                                                              'rate': 1,
                                                              'samples': [],
                                                              'sparseDataStrategy': 'None',
                                                              'sum': None,
                                                              'tags': [{'statsdType': 'ms'}],
                                                              'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.timer'].timestamp,
                                                              'unit': '',
                                                              'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_single_gauge(self):
        with self.lock:
            self.poster.submit(
                'gauge:333|g', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.gauge',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'g'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 333.0,
                                                          'cnt': 1.0,
                                                          'max': 333.0,
                                                          'metricId': 'statsd.gauge',
                                                          'min': 333.0,
                                                          'sum': 333.0,
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 333.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.gauge': {'avg': None,
                                                              'cnt': 0.0,
                                                              'max': None,
                                                              'metricType': 'GAUGE',
                                                              'min': None,
                                                              'name': 'statsd.gauge',
                                                              'orgtype': ['GAUGE'],
                                                              'samples': [333.0],
                                                              'signed': False,
                                                              'sparseDataStrategy': 'None',
                                                              'sum': None,
                                                              'tags': [{'statsdType': 'g'}],
                                                              'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.gauge'].timestamp,
                                                              'unit': '',
                                                              'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_single_histogram(self):
        with self.lock:
            self.poster.submit(
                'histogram:333|h', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.histogram',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'h'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 333.0,
                                                          'cnt': 1.0,
                                                          'max': 333.0,
                                                          'metricId': 'statsd.histogram',
                                                          'min': 333.0,
                                                          'sum': 333.0,
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 333.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.histogram': {'avg': None,
                                                                  'cnt': 0.0,
                                                                  'max': None,
                                                                  'metricType': 'GAUGE',
                                                                  'min': None,
                                                                  'name': 'statsd.histogram',
                                                                  'orgtype': ['TIMER',
                                                                              'HISTOGRAM'],
                                                                  'percentile': 0,
                                                                  'rate': 1,
                                                                  'samples': [],
                                                                  'sparseDataStrategy': 'None',
                                                                  'sum': None,
                                                                  'tags': [{'statsdType': 'h'}],
                                                                  'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.histogram'].timestamp,
                                                                  'unit': '',
                                                                  'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_single_set(self):
        with self.lock:
            self.poster.submit(
                'set:333|s', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.set',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 's'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'metricId': 'statsd.set',
                                                          'timestamp': self.poster.elements.elements['testelement'].element.samples[0].timestamp,
                                                          'val': 1.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.set': {'metricType': 'GAUGE',
                                                            'name': 'statsd.set',
                                                            'orgtype': ['SET'],
                                                            'sparseDataStrategy': 'None',
                                                            'tags': [{'statsdType': 's'}],
                                                            'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.set'].timestamp,
                                                            'unit': '',
                                                            'values': []}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_mutliple_metrics(self):

        with self.lock:
            self.poster.submit(
                'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\ncounter.tag:333|c|#tag1,tag2,tag3:value3\nset:333|s', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

                element = e.element

            j = json.loads(json.dumps(
                element, default=lambda o: o.__dict__, sort_keys=True))

            metrics_list = sorted(j['metrics'], key=lambda k: k[
                                  'id'], reverse=True)

            samples_list = list(sorted(j['samples'], key=lambda k: k[
                'metricId'], reverse=True))

            self.assertEqual(j['id'], 'testelement')
            self.assertEqual(j['type'], 'SERVER')
            self.assertEqual(j['attributes'], [])
            self.assertEqual(j['tags'], [])
            self.assertEqual(j['relations'], [])
            self.assertEqual(len(metrics_list), 7)
            self.assertEqual(len(samples_list), 7)

            self.assertEqual(samples_list,
                             [{'avg': 320.0,
                               'cnt': 1.0,
                               'max': 320.0,
                               'metricId': 'statsd.timer',
                               'min': 320.0,
                               'sum': 320.0,
                               'timestamp': element.samples[0].timestamp,
                               'val': 320.0},
                              {'metricId': 'statsd.set', 'timestamp': element.samples[
                                  0].timestamp, 'val': 1.0},
                                 {'avg': 333.0,
                                  'cnt': 1.0,
                                  'max': 333.0,
                                  'metricId': 'statsd.histogram',
                                  'min': 333.0,
                                  'sum': 333.0,
                                  'timestamp': element.samples[0].timestamp,
                                  'val': 333.0},
                                 {'avg': 333.0,
                                  'cnt': 1.0,
                                  'max': 333.0,
                                  'metricId': 'statsd.gauge',
                                  'min': 333.0,
                                  'sum': 333.0,
                                  'timestamp': element.samples[0].timestamp,
                                  'val': 333.0},
                                 {'avg': 0.1,
                                  'cnt': 1.0,
                                  'max': 0.1,
                                  'metricId': 'statsd.counterrate',
                                  'min': 0.1,
                                  'sum': 0.1,
                                  'timestamp': element.samples[0].timestamp,
                                  'val': 0.1},
                                 {'avg': 333.0,
                                  'cnt': 1.0,
                                  'max': 333.0,
                                  'metricId': 'statsd.counter.tag',
                                  'min': 333.0,
                                  'sum': 333.0,
                                  'timestamp': element.samples[0].timestamp,
                                  'val': 333.0},
                                 {'avg': 1.0,
                                  'cnt': 1.0,
                                  'max': 1.0,
                                  'metricId': 'statsd.counter',
                                  'min': 1.0,
                                  'sum': 1.0,
                                  'timestamp': element.samples[0].timestamp,
                                  'val': 1.0}]
                             )

            self.assertEqual(metrics_list, [{'id': 'statsd.timer',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 'ms'}],
                                             'type': 'GAUGE',
                                             'unit': ''},
                                            {'id': 'statsd.set',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 's'}],
                                             'type': 'GAUGE',
                                             'unit': ''},
                                            {'id': 'statsd.histogram',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 'h'}],
                                             'type': 'GAUGE',
                                             'unit': ''},
                                            {'id': 'statsd.gauge',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 'g'}],
                                             'type': 'GAUGE',
                                             'unit': ''},
                                            {'id': 'statsd.counterrate',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 'c'}],
                                             'type': 'GAUGE',
                                             'unit': ''},
                                            {'id': 'statsd.counter.tag',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 'c'},
                                                      {'name': 'tag1',
                                                          'value': None},
                                                      {'name': 'tag2',
                                                          'value': None},
                                                      {'name': 'tag3', 'value': 'value3'}],
                                             'type': 'GAUGE',
                                             'unit': ''},
                                            {'id': 'statsd.counter',
                                             'sparseDataStrategy': 'None',
                                             'tags': [{'name': 'statsdType', 'value': 'c'}],
                                             'type': 'GAUGE',
                                             'unit': ''}])

    def test_single_event(self):
        with self.lock:
            self.poster.submit(
                '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3', self.timestamp)

            j = json.loads(json.dumps(
                self.poster.events, default=lambda o: o.__dict__, sort_keys=True))

            f = [{'data': {'elementId': 'hostname', 'level': 'INFO', 'message': 'text'},
                  'source': 'netuitive-statsd',
                  'tags': [{'name': 'tag1', 'value': None},
                           {'name': 'tag2', 'value': None},
                           {'name': 'tag3', 'value': 'value3'},
                           {'name': 'priority', 'value': 'priority'},
                           {'name': 'date_happened', 'value': 'date_happened'},
                           {'name': 'aggregation_key',
                            'value': 'aggregation_key'},
                           {'name': 'source_type_name',
                            'value': 'source_type_name'},
                           {'name': 'alert_type', 'value': 'alert_type'}],
                  'timestamp': self.poster.events[0].timestamp,
                  'title': 'title',
                  'type': 'INFO'}]

            self.poster.events = []
            self.assertEqual(j, f)

    def test_single_event_minimum(self):
        with self.lock:
            self.poster.submit(
                '_e{5,4}:title|text', self.timestamp)

            j = json.loads(json.dumps(
                self.poster.events, default=lambda o: o.__dict__, sort_keys=True))

            f = [{'data': {'elementId': 'testelement', 'level': 'INFO', 'message': 'text'},
                  'source': 'netuitive-statsd',
                  'tags': [],
                  'timestamp': self.poster.events[0].timestamp,
                  'title': 'title',
                  'type': 'INFO'}]

            self.poster.events = []
            self.assertEqual(j, f)

    def test_multiple_events(self):
        with self.lock:
            self.poster.submit(
                '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3\n_e{5,4}:title|text|d:date_happened|h:hostname2|k:aggregation_key|p:critical|s:source_type_name|t:alert_type', self.timestamp)

            # for event in self.poster.events:

            j = json.loads(json.dumps(
                self.poster.events, default=lambda o: o.__dict__, sort_keys=True))

            f = [{'data': {'elementId': 'hostname', 'level': 'INFO', 'message': 'text'},
                  'source': 'netuitive-statsd',
                  'tags': [{'name': 'tag1', 'value': None},
                           {'name': 'tag2', 'value': None},
                           {'name': 'tag3', 'value': 'value3'},
                           {'name': 'priority', 'value': 'priority'},
                           {'name': 'date_happened', 'value': 'date_happened'},
                           {'name': 'aggregation_key', 'value': 'aggregation_key'},
                           {'name': 'source_type_name',
                               'value': 'source_type_name'},
                           {'name': 'alert_type', 'value': 'alert_type'}],
                  'timestamp': self.poster.events[0].timestamp,
                  'title': 'title',
                  'type': 'INFO'},
                 {'data': {'elementId': 'hostname2', 'level': 'CRITICAL', 'message': 'text'},
                  'source': 'netuitive-statsd',
                  'tags': [{'name': 'priority', 'value': 'critical'},
                           {'name': 'date_happened', 'value': 'date_happened'},
                           {'name': 'aggregation_key', 'value': 'aggregation_key'},
                           {'name': 'source_type_name',
                               'value': 'source_type_name'},
                           {'name': 'alert_type', 'value': 'alert_type'}],
                  'timestamp': self.poster.events[0].timestamp,
                  'title': 'title',
                  'type': 'INFO'}]

            self.poster.events = []
            self.assertEqual(j, f)

    def test_metric_type_change(self):

        with self.lock:

            self.poster.submit('counter:1|c', self.timestamp)
            self.poster.submit('counter:1|g', self.timestamp)

            for ename in self.poster.elements.elements:
                e = self.poster.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            element = e.element

            f = {'testelement': {'element': {'attributes': [],
                                             'id': 'testelement',
                                             'metrics': [{'id': 'statsd.counter',
                                                          'sparseDataStrategy': 'None',
                                                          'tags': [{'name': 'statsdType',
                                                                    'value': 'g'}],
                                                          'type': 'GAUGE',
                                                          'unit': ''}],
                                             'name': 'testelement',
                                             'relations': [],
                                             'samples': [{'avg': 1.0,
                                                          'cnt': 1,
                                                          'max': 1.0,
                                                          'metricId': 'statsd.counter',
                                                          'min': 1.0,
                                                          'sum': 1.0,
                                                          'timestamp': element.samples[0].timestamp,
                                                          'val': 1.0}],
                                             'tags': [],
                                             'type': 'SERVER'},
                                 'elementId': 'testelement',
                                 'metric_types': {'c': 'COUNTER',
                                                  'g': 'GAUGE',
                                                  'h': 'HISTOGRAM',
                                                  'ms': 'TIMER',
                                                  's': 'SET'},
                                 'metrics': {'statsd.counter': {'avg': None,
                                                                'cnt': 0.0,
                                                                'max': None,
                                                                'metricType': 'GAUGE',
                                                                'min': None,
                                                                'name': 'statsd.counter',
                                                                'orgtype': ['GAUGE'],
                                                                'samples': [1.0],
                                                                'signed': False,
                                                                'sparseDataStrategy': 'None',
                                                                'sum': None,
                                                                'tags': [{'statsdType': 'g'}],
                                                                'timestamp': self.poster.elements.elements['testelement'].metrics['statsd.counter'].timestamp,
                                                                'unit': '',
                                                                'value': 0.0}}}}

            self.poster.elements.delete('testelement')

            self.assertEqual(j, f)

    def test_element_type_tag(self):

        with self.lock:

            self.poster3.submit('gauge:1|g|#ty:MyType', self.timestamp)

            for ename in self.poster3.elements.elements:
                e = self.poster3.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster3.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            element = e.element

            f = {'testelement2': {'element': {'attributes': [],
                                              'id': 'testelement2',
                                              'metrics': [{'id': 'statsd.gauge',
                                                           'sparseDataStrategy': 'None',
                                                           'tags': [{'name': 'statsdType',
                                                                     'value': 'g'}],
                                                           'type': 'GAUGE',
                                                           'unit': ''}],
                                              'name': 'testelement2',
                                              'relations': [],
                                              'samples': [{'avg': 1.0,
                                                           'cnt': 1,
                                                           'max': 1.0,
                                                           'metricId': 'statsd.gauge',
                                                           'min': 1.0,
                                                           'sum': 1.0,
                                                           'timestamp': element.samples[0].timestamp,
                                                           'val': 1.0}],
                                              'tags': [],
                                              'type': 'MyType'},
                                  'elementId': 'testelement2',
                                  'metric_types': {'c': 'COUNTER',
                                                   'g': 'GAUGE',
                                                   'h': 'HISTOGRAM',
                                                   'ms': 'TIMER',
                                                   's': 'SET'},
                                  'metrics': {'statsd.gauge': {'avg': None,
                                                               'cnt': 0.0,
                                                               'max': None,
                                                               'metricType': 'GAUGE',
                                                               'min': None,
                                                               'name': 'statsd.gauge',
                                                               'orgtype': ['GAUGE'],
                                                               'samples': [1.0],
                                                               'signed': False,
                                                               'sparseDataStrategy': 'None',
                                                               'sum': None,
                                                               'tags': [{'statsdType': 'g'}],
                                                               'timestamp': self.poster3.elements.elements['testelement2'].metrics['statsd.gauge'].timestamp,
                                                               'unit': '',
                                                               'value': 0.0}}}}

            self.poster3.elements.delete('testelement2')
            self.assertEqual(j, f)

    def test_element_type(self):

        with self.lock:

            self.poster3.submit('gauge:1|g', self.timestamp)

            for ename in self.poster3.elements.elements:
                e = self.poster3.elements.elements[ename]
                e.prepare()

            j = json.loads(json.dumps(
                self.poster3.elements.elements, default=lambda o: o.__dict__,
                sort_keys=True))

            element = e.element

            f = {'testelement2': {'element': {'attributes': [],
                                              'id': 'testelement2',
                                              'metrics': [{'id': 'statsd.gauge',
                                                           'sparseDataStrategy': 'None',
                                                           'tags': [{'name': 'statsdType',
                                                                     'value': 'g'}],
                                                           'type': 'GAUGE',
                                                           'unit': ''}],
                                              'name': 'testelement2',
                                              'relations': [],
                                              'samples': [{'avg': 1.0,
                                                           'cnt': 1,
                                                           'max': 1.0,
                                                           'metricId': 'statsd.gauge',
                                                           'min': 1.0,
                                                           'sum': 1.0,
                                                           'timestamp': element.samples[0].timestamp,
                                                           'val': 1.0}],
                                              'tags': [],
                                              'type': 'NOTSERVER'},
                                  'elementId': 'testelement2',
                                  'metric_types': {'c': 'COUNTER',
                                                   'g': 'GAUGE',
                                                   'h': 'HISTOGRAM',
                                                   'ms': 'TIMER',
                                                   's': 'SET'},
                                  'metrics': {'statsd.gauge': {'avg': None,
                                                               'cnt': 0.0,
                                                               'max': None,
                                                               'metricType': 'GAUGE',
                                                               'min': None,
                                                               'name': 'statsd.gauge',
                                                               'orgtype': ['GAUGE'],
                                                               'samples': [1.0],
                                                               'signed': False,
                                                               'sparseDataStrategy': 'None',
                                                               'sum': None,
                                                               'tags': [{'statsdType': 'g'}],
                                                               'timestamp': self.poster3.elements.elements['testelement2'].metrics['statsd.gauge'].timestamp,
                                                               'unit': '',
                                                               'value': 0.0}}}}

            self.poster3.elements.delete('testelement2')
            self.assertEqual(j, f)

    @mock.patch('netuitive.client.urllib2.urlopen')
    def test_sample_cleared(self, mock_post):

        mock_post.return_value = MockResponse(code=200)

        with self.lock:
            self.poster4.submit('counter:1|c', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host1', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host2', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host3', self.timestamp)

            self.poster4.submit('counter:1|c', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host1', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host2', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host3', self.timestamp)

            for ename in self.poster4.elements.elements:
                e = self.poster4.elements.elements[ename]
                e.prepare()

            j = self.poster4.elements

            # everything should have 1 sample
            self.assertEqual(
                len(j['elements']['testelement']['element']['samples']), 1)

            self.assertEqual(
                len(j['elements']['host1']['element']['samples']), 1)

            self.assertEqual(
                len(j['elements']['host2']['element']['samples']), 1)

            self.assertEqual(
                len(j['elements']['host3']['element']['samples']), 1)

            # everything should have 1 metric
            self.assertEqual(
                len(j['elements']['testelement']['element']['metrics']), 1)

            self.assertEqual(
                len(j['elements']['host1']['element']['metrics']), 1)

            self.assertEqual(
                len(j['elements']['host2']['element']['metrics']), 1)

            self.assertEqual(
                len(j['elements']['host3']['element']['metrics']), 1)

            self.poster4.flush()

            j = self.poster4.elements

            self.assertEqual(
                len(j['elements']['testelement']['element']['samples']), 0)

            self.assertEqual(
                len(j['elements']['host1']['element']['samples']), 0)

            self.assertEqual(
                len(j['elements']['host2']['element']['samples']), 0)

            self.assertEqual(
                len(j['elements']['host3']['element']['samples']), 0)

            # everything should have 0 metric
            self.assertEqual(
                len(j['elements']['testelement']['element']['metrics']), 0)

            self.assertEqual(
                len(j['elements']['host1']['element']['metrics']), 0)

            self.assertEqual(
                len(j['elements']['host2']['element']['metrics']), 0)

            self.assertEqual(
                len(j['elements']['host3']['element']['metrics']), 0)

            self.poster4.elements.delete('testelement')
            self.poster4.elements.delete('host1')
            self.poster4.elements.delete('host2')
            self.poster4.elements.delete('host3')

    @mock.patch('netuitive.client.urllib2.urlopen')
    def test_sample_cleared(self, mock_post):

        mock_post.return_value = MockResponse(code=200)

        with self.lock:
            self.poster4.submit('counter:1|c', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host1', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host2', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host3', self.timestamp)

            self.poster4.submit('counter:1|c', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host1', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host2', self.timestamp)
            self.poster4.submit('counter:1|c|#h:host3', self.timestamp)

            for ename in self.poster4.elements.elements:
                e = self.poster4.elements.elements[ename]
                e.prepare()

            j = self.poster4.elements

            # everything should have 1 sample
            self.assertEqual(
                len(j.elements['testelement'].element.samples), 1)

            self.assertEqual(
                len(j.elements['host1'].element.samples), 1)

            self.assertEqual(
                len(j.elements['host2'].element.samples), 1)

            self.assertEqual(
                len(j.elements['host3'].element.samples), 1)

            # everything should have 1 metric
            self.assertEqual(
                len(j.elements['testelement'].element.metrics), 1)

            self.assertEqual(
                len(j.elements['host1'].element.metrics), 1)

            self.assertEqual(
                len(j.elements['host2'].element.metrics), 1)

            self.assertEqual(
                len(j.elements['host3'].element.metrics), 1)

            self.poster4.flush()

            j = self.poster4.elements

            self.assertEqual(
                len(j.elements['testelement'].element.samples), 0)

            self.assertEqual(len(j.elements['host1'].element.samples), 0)

            self.assertEqual(len(j.elements['host2'].element.samples), 0)

            self.assertEqual(len(j.elements['host3'].element.samples), 0)

            # everything should have 0 metric
            self.assertEqual(
                len(j.elements['testelement'].element.metrics), 0)

            self.assertEqual(
                len(j.elements['host1'].element.metrics), 0)

            self.assertEqual(
                len(j.elements['host2'].element.metrics), 0)

            self.assertEqual(
                len(j.elements['host3'].element.metrics), 0)

            self.poster4.elements.delete('testelement')
            self.poster4.elements.delete('host1')
            self.poster4.elements.delete('host2')
            self.poster4.elements.delete('host3')

    @mock.patch('libs.poster.logger')
    def test_memory_safety(self, mock_logging):

        with self.lock:
            self.poster5.submit('counter:1|c', self.timestamp)
            self.poster5.submit('counter:1|c|#h:host1', self.timestamp)
            self.poster5.submit('counter:1|c|#h:host2', self.timestamp)
            self.poster5.submit('counter:1|c|#h:host3', self.timestamp)

            self.poster5.submit('counter:1|c', self.timestamp)
            self.poster5.submit('counter:1|c|#h:host1', self.timestamp)
            self.poster5.submit('counter:1|c|#h:host2', self.timestamp)
            self.poster5.submit('counter:1|c|#h:host3', self.timestamp)

            for ename in self.poster5.elements.elements:
                e = self.poster5.elements.elements[ename]
                e.prepare()

            j = self.poster5.elements

            # everything should have 1 sample
            self.assertEqual(
                len(j.elements['testelement'].element.samples), 1)

            self.assertEqual(
                len(j.elements['host1'].element.samples), 1)

            self.assertEqual(
                len(j.elements['host2'].element.samples), 1)

            self.assertEqual(
                len(j.elements['host3'].element.samples), 1)

            # everything should have 1 metric
            self.assertEqual(
                len(j.elements['testelement'].element.metrics), 1)

            self.assertEqual(
                len(j.elements['host1'].element.metrics), 1)

            self.assertEqual(
                len(j.elements['host2'].element.metrics), 1)

            self.assertEqual(
                len(j.elements['host3'].element.metrics), 1)

            self.poster5.flush_error_count = 901
            self.poster5.flush()

            self.assertEqual(mock_logging.error.call_args_list[0][0][0],
                             "failed to post for at least 900 seconds. dropping data to prevent memory starvation.")

            j = self.poster5.elements

            self.assertEqual(len(j.elements), 1)
            self.assertEqual(len(j.elements['testelement'].metrics), 0)

            # self.poster5.elements.delete_all()

    def tearDown(self):
        self.poster.stop()
        self.poster2.stop()
        self.poster3.stop()
        self.poster4.stop()
        self.poster5.stop()

if __name__ == '__main__':
    unittest.main()
