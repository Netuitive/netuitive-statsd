#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitivestatsd` module.
"""

import unittest
import logging
import threading

import libs
logging.basicConfig()
logging.disable(logging.ERROR)


class Test_Aggregation(unittest.TestCase):
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

        self.timestamp = 1434110794
        self.myElement = libs.Element(self.config['hostname'])
        self.poster = libs.Poster(self.config, self.myElement)
        self.poster.start()

        self.lock = threading.Lock()

    def test_gauge_aggregate_unsigned(self):

        with self.lock:
            self.poster.submit(
                'gauge:10|g\ngauge:11|g\ngauge:3|g', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.gauge'].samples)

            e.prepare()

            # this should have 1 value
            prepared_samples = list(e.metrics['statsd.gauge'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [10.0, 11.0, 3.0])
            self.assertEqual(prepared_samples, [3.0])
            self.assertEqual(samples_to_post, {'avg': 8.0,
                                               'cnt': 3.0,
                                               'max': 11.0,
                                               'metricId': 'statsd.gauge',
                                               'min': 3.0,
                                               'sum': 24.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 3.0})

    def test_gauge_aggregate_signed(self):

        with self.lock:
            self.poster.submit(
                'gauge:+10|g\ngauge:+11|g\ngauge:-3|g', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.gauge'].samples)

            e.prepare()

            # this should have 1 value
            prepared_samples = list(e.metrics['statsd.gauge'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [10.0, 21.0, 18.0])
            self.assertEqual(prepared_samples, [18.0])
            self.assertEqual(samples_to_post, {'avg': 16.333333333333332,
                                               'cnt': 3.0,
                                               'max': 21.0,
                                               'metricId': 'statsd.gauge',
                                               'min': 10.0,
                                               'sum': 49.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 18.0})

    def test_gauge_aggregate_unsigned_and_signed(self):

        with self.lock:
            self.poster.submit(
                'gauge:10|g\ngauge:11|g\ngauge:-3|g', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.gauge'].samples)

            e.prepare()

            # this should have 1 value
            prepared_samples = list(e.metrics['statsd.gauge'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [10.0, 11.0, 8.0])
            self.assertEqual(prepared_samples, [8.0])
            self.assertEqual(samples_to_post, {'avg': 9.666666666666666,
                                               'cnt': 3.0,
                                               'max': 11.0,
                                               'metricId': 'statsd.gauge',
                                               'min': 8.0,
                                               'sum': 29.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 8.0})

    def test_counter_aggregate_test1(self):

        with self.lock:
            self.poster.submit(
                'counter:10|c\ncounter:1|c\ncounter:10|c', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.counter'].samples)

            e.prepare()

            # this should have 0 values
            prepared_samples = list(e.metrics['statsd.counter'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [10.0, 1.0, 10.0])
            self.assertEqual(prepared_samples, [])
            self.assertEqual(samples_to_post, {'avg': 21.0 / 3.0,
                                               'cnt': 3.0,
                                               'max': 10.0,
                                               'metricId': 'statsd.counter',
                                               'min': 1.0,
                                               'sum': 21.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 21.0})

    def test_counter_aggregate_test2(self):

        with self.lock:
            self.poster.submit(
                'counter:-10|c\ncounter:1|c\ncounter:20|c', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.counter'].samples)

            e.prepare()

            # this should have 0 values
            prepared_samples = list(e.metrics['statsd.counter'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [-10.0, 1.0, 20.0])
            self.assertEqual(prepared_samples, [])
            self.assertEqual(samples_to_post, {'avg': 11.0 / 3.0,
                                               'cnt': 3.0,
                                               'max': 20.0,
                                               'metricId': 'statsd.counter',
                                               'min': -10.0,
                                               'sum': 11.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 11.0})

    def test_counter_aggregate_test3(self):

        with self.lock:
            self.poster.submit(
                'counter:2|c\ncounter:5|c\ncounter:3|c', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.counter'].samples)

            e.prepare()

            # this should have 0 values
            prepared_samples = list(e.metrics['statsd.counter'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [2.0, 5.0, 3.0])
            self.assertEqual(prepared_samples, [])
            self.assertEqual(samples_to_post, {'avg': 10.0 / 3.0,
                                               'cnt': 3.0,
                                               'max': 5.0,
                                               'metricId': 'statsd.counter',
                                               'min': 2.0,
                                               'sum': 10.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 10.0})

    def test_timer_aggregate(self):
        with self.lock:
            self.poster.submit(
                'timer:10|ms\ntimer:1|ms\ntimer:10|ms', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.timer'].samples)

            e.prepare()

            # this should have 0 values
            prepared_samples = list(e.metrics['statsd.timer'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [10.0, 1.0, 10.0])
            self.assertEqual(prepared_samples, [])
            self.assertEqual(samples_to_post, {'avg': 7.0,
                                               'cnt': 3.0,
                                               'max': 10.0,
                                               'metricId': 'statsd.timer',
                                               'min': 1.0,
                                               'sum': 21.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 21.0})

    def test_histogram_aggregate(self):
        with self.lock:
            self.poster.submit(
                'histogram:10|h\nhistogram:1|h\nhistogram:10|h', self.timestamp)

            e = self.poster.elements.elements['testelement']

            # internal list of samples
            samples = list(e.metrics['statsd.histogram'].samples)

            e.prepare()

            # this should have 0 values
            prepared_samples = list(e.metrics['statsd.histogram'].samples)

            # the samples used to build the payload
            samples_to_post = e.element.samples[0].__dict__

            self.assertListEqual(samples, [10.0, 1.0, 10.0])
            self.assertEqual(prepared_samples, [])
            self.assertEqual(samples_to_post, {'avg': 7.0,
                                               'cnt': 3.0,
                                               'max': 10.0,
                                               'metricId': 'statsd.histogram',
                                               'min': 1.0,
                                               'sum': 21.0,
                                               'timestamp': samples_to_post['timestamp'],
                                               'val': 21.0})

    def test_set_aggregate(self):
        with self.lock:
            self.poster.submit(
                'set:111|s\nset:222|s\nset:222|s\nset:333|s', self.timestamp)

            e = self.poster.elements.elements['testelement']
            e.prepare()

            samples = e.element.samples[0].__dict__

            self.assertEqual(samples['val'], 3.0)

    def tearDown(self):
        self.poster.stop()


if __name__ == '__main__':
    unittest.main()
