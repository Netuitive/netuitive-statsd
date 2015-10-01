
import time
from decimal import Decimal

import json
import netuitive


class Gauge(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.metricType = 'gauge'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.values = {}
        self.values[self.name] = {}

    def add_value(self, value, ts):
        timestamp = int(ts)
        self.values[self.name][timestamp] = value

    def get_values(self):
        return(self.values)

    def clear(self):
        self.values.clear()


class Counter(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.metricType = 'counter'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.values = {}
        self.values[self.name] = {}
        self.value = Decimal(0)

    def add_value(self, value, ts, rate=1):
        timestamp = int(ts)
        self.value += Decimal(value * Decimal(1 / rate))
        self.values[self.name][timestamp] = self.value

    def get_values(self):
        return(self.values)

    def clear(self):
        self.value = Decimal(0)
        self.values.clear()


class Meter(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.metricType = 'counter'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.values = {}
        self.values[self.name] = {}
        self.value = 0

    def add_value(self, value, ts, rate=1):
        timestamp = int(ts)
        self.value += Decimal(value * Decimal(1 / rate))
        self.values[self.name][timestamp] = self.value

    def get_values(self):
        return(self.values)

    def clear(self):
        self.values.clear()


class Histogram(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.count = 0
        self.metricType = 'histogram'
        self.timestamp = int(time.time())
        self.last_timestamp = int(time.time())
        self.rate = 1
        self.percentile = 0
        self.samples = []

    def add_value(self, value, ts, rate=1):
        timestamp = int(ts)
        self.count += Decimal(value * Decimal(1 / rate))
        self.samples.append(value)
        self.timestamp = timestamp
        self.last_timestamp = int(time.time())

    def get_values(self):
        ret = {}

        samlen = len(self.samples)

        if samlen > 0:
            self.samples.sort()
            sammin = self.samples[0]
            sammax = self.samples[-1]
            samavg = sum(self.samples) / Decimal(samlen)
            sammed = self.samples[Decimal(round(samlen / 2 - 1))]
            samper95 = self.samples[Decimal(round(0.95 * samlen - 1))]
            samper99 = self.samples[Decimal(round(0.99 * samlen - 1))]

            timestamp = int(time.time())

            ret = {
                self.name + '.count': {timestamp: samlen},
                self.name + '.min': {timestamp: sammin},
                self.name + '.max': {timestamp: sammax},
                self.name + '.avg': {timestamp: samavg},
                self.name + '.median': {timestamp: sammed},
                self.name + '.95percentile': {timestamp: samper95},
                self.name + '.99percentile': {timestamp: samper99}
            }

        return(ret)

    def clear(self):
        self.samples = []
        self.count = 0


class Set(object):

    def __init__(self, name, sparseDataStrategy='None', unit=''):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.value = set()
        self.timestamp = int(time.time())
        self.metricType = 'set'
        self.values = {}
        self.values[self.name] = {}

    def add_value(self, value, ts):
        timestamp = int(ts)
        self.value.add(value)
        self.timestamp = timestamp

    def get_values(self):
        timestamp = int(time.time())
        self.values[self.name][timestamp] = len(self.value)
        return(self.values)

    def clear(self):
        self.value.clear()


class Element(object):

    """
    An entity that represents an element
    """

    def __init__(self, elementId, ElementType='SERVER'):
        self.element = netuitive.Element(ElementType)
        self.elementId = elementId
        self.metrics = {}

        self.metric_types = {'c': 'COUNTER',
                             'g': 'GAUGE',
                             'ms': 'TIMER',
                             's': 'SET',
                             'h': 'HISTOGRAM',
                             'm': 'METER'}

    def add_attribute(self, name, value):
        self.element.add_attribute(name, value)

    def add_tag(self, name, value):
        self.element.add_tag(name, value)

    def clear_samples(self):
        self.metrics.clear()
        self.element.clear_samples()

    def add_sample(self, metricId, ts, value, metricType, rate=1, sparseDataStrategy='None', unit=''):

        try:
            timestamp = int(ts)
            mtype = self.metric_types[metricType]

            if mtype == 'GAUGE':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Gauge(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(Decimal(value), timestamp)

            if mtype == 'COUNTER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Counter(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(
                    Decimal(value), timestamp, rate)

            if mtype == 'METER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Meter(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(
                    Decimal(value), timestamp, rate)

            if mtype == 'HISTOGRAM' or mtype == 'TIMER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Histogram(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(
                    Decimal(value), timestamp, rate)

            if mtype == 'SET':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Set(
                        metricId, sparseDataStrategy, unit)

                self.metrics[metricId].add_value(Decimal(value), timestamp)

        except Exception as e:
            raise(e)

    def prepare(self):

        try:
            for m in self.metrics:
                metrics = self.metrics[m].get_values()
                metricType = self.metrics[m].metricType
                sparseDataStrategy = self.metrics[m].sparseDataStrategy
                unit = self.metrics[m].unit

                for name in metrics:
                    for timestamp in metrics[name]:
                        value = metrics[name][timestamp]

                        self.element.add_sample(
                            name,
                            timestamp,
                            value,
                            metricType,
                            self.elementId,
                            sparseDataStrategy,
                            unit)

                metrics = self.metrics[m].clear()

        except Exception as e:
            raise(e)
