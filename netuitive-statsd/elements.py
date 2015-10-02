import time
import logging

import netuitive

logger = logging.getLogger(__name__)


class Gauge(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.metricType = 'gauge'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.value = float(0)
        self.signed = False
        self.timestamp = int(time.time())

    def add_value(self, value, ts, sign=None):
        self.timestamp = int(ts)

        if sign is None:
            self.value = float(value)

        if sign == '+':
            self.signed = True
            self.value += float(value)

        if sign == '-':
            self.signed = True
            self.value += float('-' + str(value))

    def get_values(self, ts=0):

        if ts > 0:
            timestamp = int(ts)

        else:
            timestamp = self.timestamp

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': self.value
            }
        }

        return(ret)

    def clear(self):
        if self.signed is False:
            self.value = 0


class Counter(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.metricType = 'counter'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.value = float(0)
        self.timestamp = int(time.time())

    def add_value(self, value, ts, rate=None):
        self.timestamp = int(ts)

        if rate is None:
            rate = 1.0

        self.value += value * float(1 / rate)

    def get_values(self, ts=0):
        if ts > 0:
            timestamp = int(ts)
        else:
            timestamp = self.timestamp

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': self.value
            }
        }

        return(ret)

    def clear(self):
        self.value = 0


class Histogram(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.count = 0
        self.metricType = 'histogram'
        self.timestamp = int(time.time())
        self.rate = 1
        self.percentile = 0
        self.samples = []
        self.value = float(0)

    def add_value(self, value, ts, rate=None, sign=None):
        timestamp = int(ts)

        if rate is None:
            self.value += value
        else:
            self.value += value * float(1 / rate)

        self.samples.append(value)
        self.timestamp = timestamp

    def get_values(self, ts):

        if ts > 0:
            timestamp = int(ts)

        else:
            timestamp = self.timestamp

        samlen = len(self.samples)

        if samlen > 0:
            self.samples.sort()
            sammin = float(self.samples[0])
            sammax = float(self.samples[-1])
            samavg = float(sum(self.samples) / int(samlen))
            sammed = float(self.samples[int(round(samlen / 2 - 1))])
            samper95 = float(self.samples[int(round(0.95 * samlen - 1))])
            samper99 = float(self.samples[int(round(0.99 * samlen - 1))])

            ret = {
                self.name + '.count': {
                    'timestamp': timestamp,
                    'value': samlen
                },
                self.name + '.min': {
                    'timestamp': timestamp,
                    'value': sammin
                },
                self.name + '.max': {
                    'timestamp': timestamp,
                    'value': sammax
                },
                self.name + '.avg': {
                    'timestamp': timestamp,
                    'value': samavg
                },
                self.name + '.median': {
                    'timestamp': timestamp,
                    'value': sammed
                },
                self.name + '.95percentile': {
                    'timestamp': timestamp,
                    'value': samper95
                },
                self.name + '.99percentile': {
                    'timestamp': timestamp,
                    'value': samper99
                }
            }

        return(ret)

    def clear(self):
        self.samples = []
        self.count = 0
        self.value = float(0)


class Set(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.value = set()
        self.timestamp = int(time.time())
        self.metricType = 'set'

    def add_value(self, value, ts, sign=None):
        timestamp = int(ts)
        self.value.add(value)
        self.timestamp = timestamp

    def get_values(self, ts=0):
        if ts > 0:
            timestamp = int(ts)

        else:
            timestamp = self.timestamp

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': float(len(self.value))
            }
        }

        return(ret)

    def clear(self):
        self.value.clear()


class Element(object):

    """
    An entity that represents an element
    """

    def __init__(self, elementId, ElementType='SERVER'):
        logger.debug('__init__ for Element')

        self.element = netuitive.Element(ElementType)
        self.elementId = elementId
        self.metrics = {}

        self.metric_types = {'c': 'COUNTER',
                             'g': 'GAUGE',
                             'ms': 'TIMER',
                             's': 'SET',
                             'h': 'HISTOGRAM'}

    def add_attribute(self, name, value):
        self.element.add_attribute(name, value)

    def add_tag(self, name, value):
        self.element.add_tag(name, value)

    def clear_samples(self):
        self.metrics.clear()
        self.element.clear_samples()

    def add_sample(self, metricId, ts, value, metricType, sign=None, rate=None, sparseDataStrategy='None', unit=''):

        logger.debug('add_sample')

        try:
            timestamp = int(ts)
            mtype = self.metric_types[metricType]

            if mtype == 'GAUGE':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Gauge(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(value, timestamp, sign)

            if mtype == 'COUNTER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Counter(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(
                    value, timestamp, rate)

            if mtype == 'HISTOGRAM' or mtype == 'TIMER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Histogram(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(
                    value, timestamp, rate)

            if mtype == 'SET':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Set(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(value, timestamp)

        except Exception as e:
            raise(e)

    def prepare(self):

        try:
            logger.debug('starting prepare')
            for m in self.metrics:
                metrics = self.metrics[m].get_values(int(time.time()))
                metricType = self.metrics[m].metricType
                sparseDataStrategy = self.metrics[m].sparseDataStrategy
                unit = self.metrics[m].unit

                for name in metrics:
                    timestamp = metrics[name]['timestamp']
                    value = float(metrics[name]['value'])

                    self.element.add_sample(
                        name,
                        timestamp,
                        value,
                        metricType,
                        self.elementId,
                        sparseDataStrategy,
                        unit)

                metrics = self.metrics[m].clear()

            logger.debug('finished prepare')

        except Exception as e:
            raise(e)
