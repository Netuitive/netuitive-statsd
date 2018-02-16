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
                       'url': 'http://test.com',
                       'no_internal_metrics': False}

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
                        'url': 'http://test.com',
                        'no_internal_metrics': True}

        self.timestamp = 1434110794002
        self.lock = threading.Lock()

    def test_Poster_config(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        element2 = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster2 = libs.Poster(self.config, element2, 8)
        poster2.start()

        self.assertEqual(poster.api.agent, 'Netuitive-Statsd/develop')
        self.assertEqual(poster2.api.agent, 'Netuitive-Statsd/8')

        poster.stop()
        poster.join()
        poster2.stop()
        poster2.join()

    def test_single_counter(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit('counter:1|c', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                            'timestamp': poster.elements.elements['testelement'].metrics['statsd.counter'].timestamp,
                                                            'unit': '',
                                                            'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_single_counter_with_tags(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'counter:1|c|#tag1,tag2,tag3:value3', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                            'timestamp': poster.elements.elements['testelement'].metrics['statsd.counter'].timestamp,
                                                            'unit': '',
                                                            'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_single_counter_with_rate(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'counterrate:1|c|@0.1', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                                'timestamp': poster.elements.elements['testelement'].metrics['statsd.counterrate'].timestamp,
                                                                'unit': '',
                                                                'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_single_timer(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'timer:320|ms', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                          'timestamp': poster.elements.elements['testelement'].metrics['statsd.timer'].timestamp,
                                                          'unit': '',
                                                          'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_single_gauge(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'gauge:333|g', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                          'timestamp': poster.elements.elements['testelement'].metrics['statsd.gauge'].timestamp,
                                                          'unit': '',
                                                          'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_single_histogram(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'histogram:333|h', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                              'timestamp': poster.elements.elements['testelement'].metrics['statsd.histogram'].timestamp,
                                                              'unit': '',
                                                              'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_single_set(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'set:333|s', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                      'timestamp': poster.elements.elements['testelement'].element.samples[0].timestamp,
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
                                                        'timestamp': poster.elements.elements['testelement'].metrics['statsd.set'].timestamp,
                                                        'unit': '',
                                                        'values': []}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_mutliple_metrics(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            'counter:1|c\ncounterrate:1|c|@0.1\ntimer:320|ms\ngauge:333|g\nhistogram:333|h\ncounter.tag:333|c|#tag1,tag2,tag3:value3\nset:333|s', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

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
                           'timestamp': samples_list[0]['timestamp'],
                           'val': 320.0},
                          {'metricId': 'statsd.set', 'timestamp': samples_list[
                              1]['timestamp'], 'val': 1.0},
                             {'avg': 333.0,
                              'cnt': 1.0,
                              'max': 333.0,
                              'metricId': 'statsd.histogram',
                              'min': 333.0,
                              'sum': 333.0,
                              'timestamp': samples_list[2]['timestamp'],
                              'val': 333.0},
                             {'avg': 333.0,
                              'cnt': 1.0,
                              'max': 333.0,
                              'metricId': 'statsd.gauge',
                              'min': 333.0,
                              'sum': 333.0,
                              'timestamp': samples_list[3]['timestamp'],
                              'val': 333.0},
                             {'avg': 0.1,
                              'cnt': 1.0,
                              'max': 0.1,
                              'metricId': 'statsd.counterrate',
                              'min': 0.1,
                              'sum': 0.1,
                              'timestamp': samples_list[4]['timestamp'],
                              'val': 0.1},
                             {'avg': 333.0,
                              'cnt': 1.0,
                              'max': 333.0,
                              'metricId': 'statsd.counter.tag',
                              'min': 333.0,
                              'sum': 333.0,
                              'timestamp': samples_list[5]['timestamp'],
                              'val': 333.0},
                             {'avg': 1.0,
                              'cnt': 1.0,
                              'max': 1.0,
                              'metricId': 'statsd.counter',
                              'min': 1.0,
                              'sum': 1.0,
                              'timestamp': samples_list[6]['timestamp'],
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

        poster.stop()
        poster.join()

    def test_single_event(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3', self.timestamp)

        j = json.loads(json.dumps(
            poster.events, default=lambda o: o.__dict__, sort_keys=True))

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
              'timestamp': poster.events[0].timestamp,
              'title': 'title',
              'type': 'INFO'}]

        poster.events = []
        self.assertEqual(j, f)
        poster.stop()
        poster.join()

    def test_single_event_minimum(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            '_e{5,4}:title|text', self.timestamp)

        j = json.loads(json.dumps(
            poster.events, default=lambda o: o.__dict__, sort_keys=True))

        f = [{'data': {'elementId': 'testelement', 'level': 'INFO', 'message': 'text'},
              'source': 'netuitive-statsd',
              'tags': [],
              'timestamp': poster.events[0].timestamp,
              'title': 'title',
              'type': 'INFO'}]

        poster.events = []
        self.assertEqual(j, f)
        poster.stop()
        poster.join()

    def test_multiple_events(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit(
            '_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3\n_e{5,4}:title|text|d:date_happened|h:hostname2|k:aggregation_key|p:critical|s:source_type_name|t:alert_type', self.timestamp)

        # for event in poster.events:

        j = json.loads(json.dumps(
            poster.events, default=lambda o: o.__dict__, sort_keys=True))

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
              'timestamp': poster.events[0].timestamp,
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
              'timestamp': poster.events[0].timestamp,
              'title': 'title',
              'type': 'INFO'}]

        poster.events = []
        self.assertEqual(j, f)
        poster.stop()
        poster.join()

    def test_metric_type_change(self):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit('counter:1|c', self.timestamp)
        poster.submit('counter:1|g', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                            'timestamp': poster.elements.elements['testelement'].metrics['statsd.counter'].timestamp,
                                                            'unit': '',
                                                            'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_element_type_tag(self):

        element = libs.Element(
            self.config2['hostname'], self.config2['element_type'])
        poster = libs.Poster(self.config2, element)
        poster.start()

        poster.submit('gauge:1|g|#ty:MyType', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                           'timestamp': poster.elements.elements['testelement2'].metrics['statsd.gauge'].timestamp,
                                                           'unit': '',
                                                           'value': 0.0}}}}

        poster.stop()
        poster.join()
        self.assertEqual(j, f)

    def test_element_type(self):

        element = libs.Element(
            self.config2['hostname'], self.config2['element_type'])
        poster = libs.Poster(self.config2, element)
        poster.start()

        poster.submit('gauge:1|g', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
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
                                                           'timestamp': poster.elements.elements['testelement2'].metrics['statsd.gauge'].timestamp,
                                                           'unit': '',
                                                           'value': 0.0}}}}

        poster.stop()
        poster.join()
        self.assertEqual(j, f)

    def test_metric_unit_tag(self):

        element = libs.Element(
            self.config2['hostname'], self.config2['element_type'])
        poster = libs.Poster(self.config2, element)
        poster.start()

        poster.submit('gauge:1|g|#un:ms', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
            sort_keys=True))

        element = e.element

        f = {'testelement2': {'element': {'attributes': [],
                                          'id': 'testelement2',
                                          'metrics': [{'id': 'statsd.gauge',
                                                       'sparseDataStrategy': 'None',
                                                       'tags': [{'name': 'statsdType',
                                                                 'value': 'g'},
                                                                {'name': 'un',
                                                                 'value': 'ms'}],
                                                       'type': 'GAUGE',
                                                       'unit': 'ms'}],
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
                                                           'tags': [{'statsdType': 'g'},
                                                                    {'un': 'ms'}],
                                                           'timestamp': poster.elements.elements['testelement2'].metrics['statsd.gauge'].timestamp,
                                                           'unit': 'ms',
                                                           'value': 0.0}}}}

        poster.stop()
        poster.join()

        self.assertEqual(j, f)

    def test_metric_unit_and_type_tag(self):

        element = libs.Element(
            self.config2['hostname'], self.config2['element_type'])
        poster = libs.Poster(self.config2, element)
        poster.start()

        poster.submit('gauge:1|g|#ty:APP,un:ms', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = json.loads(json.dumps(
            poster.elements.elements, default=lambda o: o.__dict__,
            sort_keys=True))

        element = e.element

        f = {'testelement2': {'element': {'attributes': [],
                                          'id': 'testelement2',
                                          'metrics': [{'id': 'statsd.gauge',
                                                       'sparseDataStrategy': 'None',
                                                       'tags': [{'name': 'statsdType',
                                                                 'value': 'g'},
                                                                {'name': 'un',
                                                                 'value': 'ms'}],
                                                       'type': 'GAUGE',
                                                       'unit': 'ms'}],
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
                                          'type': 'APP'},
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
                                                           'tags': [{'statsdType': 'g'},
                                                                    {'un': 'ms'}],
                                                           'timestamp': poster.elements.elements['testelement2'].metrics['statsd.gauge'].timestamp,
                                                           'unit': 'ms',
                                                           'value': 0.0}}}}

        poster.stop()
        poster.join()
        self.assertEqual(j, f)

    @mock.patch('netuitive.client.urllib2.urlopen')
    def test_sample_cleared(self, mock_post):

        mock_post.return_value = MockResponse(code=200)

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit('counter:1|c', self.timestamp)
        poster.submit('counter:1|c|#h:host1', self.timestamp)
        poster.submit('counter:1|c|#h:host2', self.timestamp)
        poster.submit('counter:1|c|#h:host3', self.timestamp)

        poster.submit('counter:1|c', self.timestamp)
        poster.submit('counter:1|c|#h:host1', self.timestamp)
        poster.submit('counter:1|c|#h:host2', self.timestamp)
        poster.submit('counter:1|c|#h:host3', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = poster.elements

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

        poster.flush()

        j = poster.elements

        self.assertEqual(
            len(j.elements['testelement'].element.samples), 0)

        self.assertEqual(
            len(j.elements['testelement'].element.metrics), 0)

        # there will no longer be cached elements created from 'h' tags
        self.assertNotIn('host1', j.elements.keys())

        self.assertNotIn('host2', j.elements.keys())

        self.assertNotIn('host3', j.elements.keys())

        poster.stop()
        poster.join()

    @mock.patch('libs.poster.logger')
    def test_memory_safety(self, mock_logging):

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()

        poster.submit('counter:1|c', self.timestamp)
        poster.submit('counter:1|c|#h:host1', self.timestamp)
        poster.submit('counter:1|c|#h:host2', self.timestamp)
        poster.submit('counter:1|c|#h:host3', self.timestamp)

        poster.submit('counter:1|c', self.timestamp)
        poster.submit('counter:1|c|#h:host1', self.timestamp)
        poster.submit('counter:1|c|#h:host2', self.timestamp)
        poster.submit('counter:1|c|#h:host3', self.timestamp)

        for ename in poster.elements.elements:
            e = poster.elements.elements[ename]
            e.prepare()
            e.element.merge_metrics()

        j = poster.elements

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

        poster.flush_error_count = 901
        poster.flush()

        self.assertEqual(mock_logging.error.call_args_list[0][0][0],
                         "failed to post for at least 900 seconds. dropping data to prevent memory starvation.")

        j = poster.elements

        self.assertEqual(len(j.elements), 1)
        self.assertEqual(len(j.elements['testelement'].metrics), 0)
        poster.stop()
        poster.join()

    @mock.patch('netuitive.client.urllib2.urlopen')
    def test_no_internal_metrics_default(self, mock_post):

        mock_post.return_value = MockResponse(code=200)

        element = libs.Element(
            self.config['hostname'], self.config['element_type'])
        poster = libs.Poster(self.config, element)
        poster.start()
        poster.submit('counter:1|c', self.timestamp)
        poster.flush()

        data = mock_post.call_args_list[0][0][0].data

        a = []
        b = json.loads(data)[0]['metrics']
        for c in b:
            a.append(c['id'])

        d = sorted(a)

        e = sorted(['statsd.counter',
                    'statsd.netuitive-statsd.samples_received.count',
                    'statsd.netuitive-statsd.packets_received.count',
                    'statsd.netuitive-statsd.event_received.count'])

        poster.stop()
        poster.join()
        self.assertListEqual(d, e)

    @mock.patch('netuitive.client.urllib2.urlopen')
    def test_no_internal_metrics_disabled(self, mock_post):

        mock_post.return_value = MockResponse(code=200)

        element = libs.Element(
            self.config2['hostname'], self.config2['element_type'])
        poster = libs.Poster(self.config2, element)
        poster.start()
        poster.submit('counter:1|c', self.timestamp)
        poster.flush()

        data = mock_post.call_args_list[0][0][0].data

        a = []
        b = json.loads(data)[0]['metrics']
        for c in b:
            a.append(c['id'])

        d = sorted(a)

        e = sorted(['statsd.counter'])

        poster.stop()
        poster.join()
        self.assertListEqual(d, e)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
