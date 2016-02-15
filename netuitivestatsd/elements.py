import time
import logging

import netuitive

logger = logging.getLogger(__name__)


class Gauge(object):

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.metricType = 'GAUGE'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
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
            self.value -= float(value)

    def get_values(self, ts=0):

        if ts > 0:
            timestamp = int(ts)

        else:
            timestamp = int(time.time())

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

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.metricType = 'GAUGE'
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
        self.value = float(0)
        self.timestamp = int(time.time())

    def add_value(self, value, ts, rate=None):
        self.timestamp = int(ts)

        if rate is None:
            rate = 1.0

        self.value += value * float(rate)

    def get_values(self, ts=0):
        if ts > 0:
            timestamp = int(ts)
        else:
            timestamp = int(time.time())

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

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
        self.metricType = 'GAUGE'
        self.timestamp = int(time.time())
        self.rate = 1
        self.percentile = 0
        self.samples = []
        self.value = float(0)
        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = 0
        self.per95 = None
        self.per99 = None

    def add_value(self, value, ts, rate=None, sign=None):
        timestamp = int(ts)

        if rate is None:
            self.value += value
        else:
            self.value += value * float(rate)

        self.samples.append(value)
        self.timestamp = timestamp

    def get_values(self, ts):

        if ts > 0:
            timestamp = int(ts)

        else:
            timestamp = int(time.time())

        samlen = len(self.samples)

        if samlen > 0:
            self.samples.sort()
            self.cnt = samlen
            self.sum = sum(self.samples)
            self.min = float(self.samples[0])
            self.max = float(self.samples[-1])
            self.avg = float(sum(self.samples) / int(samlen))
            self.med = float(self.samples[int(round(samlen / 2 - 1))])
            self.per95 = float(self.samples[int(round(0.95 * samlen - 1))])
            self.per99 = float(self.samples[int(round(0.99 * samlen - 1))])

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': self.value,
                'avg': self.avg,
                'cnt': self.cnt,
                'max': self.max,
                'min': self.min,
                'sum': self.sum
            }
        }

        return(ret)

    def clear(self):
        self.samples = []
        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = 0
        self.per95 = None
        self.per99 = None
        self.value = float(0)


class Set(object):

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
        self.values = []
        self.timestamp = int(time.time())
        self.metricType = 'GAUGE'

    def add_value(self, value, ts, sign=None):
        timestamp = int(ts)
        value = 2
        if str(value) not in self.values:
            self.values.append(str(value))

        self.timestamp = timestamp

    def get_values(self, ts=0):
        if ts > 0:
            timestamp = int(ts)

        else:
            timestamp = int(time.time())

        value = float(len(self.values))

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': value
            }
        }

        return(ret)

    def clear(self):
        self.values = []


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

    def add_sample(self, metricId, ts, value, metricType, sign=None, rate=None, tags=[]):

        logger.debug('add_sample')

        unit = ''
        sparseDataStrategy = 'None'

        try:

            timestamp = int(ts)
            mtype = self.metric_types[metricType]

            # # reserved tags
            for t in tags:

                if 'unit' in t:
                    unit = t['unit']

                if 'sparseDataStrategy' in t:
                    sparseDataStrategy = t['sparseDataStrategy']

            if mtype == 'GAUGE':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Gauge(
                        metricId, sparseDataStrategy, unit, tags)

                self.metrics[metricId].add_value(value, timestamp, sign)

            if mtype == 'COUNTER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Counter(
                        metricId, sparseDataStrategy, unit, tags)

                self.metrics[metricId].add_value(
                    value, timestamp, rate)

            if mtype == 'HISTOGRAM' or mtype == 'TIMER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Histogram(
                        metricId, sparseDataStrategy, unit, tags)

                self.metrics[metricId].add_value(
                    value, timestamp, rate)

            if mtype == 'SET':
                if metricId not in self.metrics:
                    self.metrics[metricId] = Set(
                        metricId, sparseDataStrategy, unit, tags)

                self.metrics[metricId].add_value(value, timestamp)

        except Exception as e:
            raise(e)

    def prepare(self):

        try:
            logger.debug('starting prepare')
            for m in self.metrics:

                metric = self.metrics[m]
                samples = metric.get_values(int(time.time()))
                metricType = metric.metricType
                sparseDataStrategy = metric.sparseDataStrategy
                unit = metric.unit

                tags = metric.tags

                if len(tags) == 0:
                    tags = None

                for name in samples:
                    d = samples[name]
                    mmin = None
                    mmax = None
                    mavg = None
                    msum = None
                    mcnt = None

                    timestamp = d['timestamp']
                    value = float(d['value'])

                    if 'min' in d:
                        mmin = d['min']

                    if 'max' in d:
                        mmax = d['max']

                    if 'avg' in d:
                        mavg = d['avg']

                    if 'sum' in d:
                        msum = d['sum']

                    if 'cnt' in d:
                        mcnt = d['cnt']

                    self.element.add_sample(
                        name,
                        timestamp,
                        value,
                        metricType,
                        self.elementId,
                        sparseDataStrategy,
                        unit,
                        tags,
                        mmin,
                        mmax,
                        mavg,
                        msum,
                        mcnt)

                    metric.clear()

            logger.debug('finished prepare')

        except Exception as e:
            raise(e)
