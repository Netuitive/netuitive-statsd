#!/usr/bin/env python2.7
# --*-- Encoding: UTF-8 --*--
"""Usage:
        netuitive-statsd [-d] -c CONFIG <command>

        netuitive-statsd -h | --help
        netuitive-statsd --version

Description:
        Netuitive StatsD server

Examples:
        examples would be awesome
Options:
    -c CONFIG --configfile=CONFIG    Config file
    -d --debug    Enable debug output
    -h --help     Show this screen.
    --version     Show version.
"""

from __future__ import unicode_literals, print_function
import logging
import logging.config
import os
import select
import signal
import socket
import sys
import threading
import time
import urllib2
import json
import platform
import datetime
import re
import traceback

import configobj
import psutil
from docopt import docopt
import docker
from netuitivestatsd.daemon import Daemon
from setproctitle import setproctitle
import netuitive

from netuitivestatsd.elements import Element
from netuitivestatsd.statsd import parse_message

# Constants
__version__ = "0.0.1"
__author__ = "Netuitive, Inc."
__license__ = "Apache 2.0"

logger = logging.getLogger()


# default config
CONFIG = {
    'url': 'https//api.app.netuitive.com/ingest',
    'hostname': socket.gethostname(),
    'listen_ip': '127.0.0.1',
    'listen_port': 8125,
    'forward_ip': '',
    'forward_port': 8125,
    'element_type': 'DEFAULT',
    'forward': False,
    'interval': 60,
    'pid_file': 'netuitive-stats.pid',
    'log_file': 'netuitive-statsd.log',
    'debug': False
}


def extract_function_name():
    """Extracts failing function name from Traceback
    by Alex Martelli
    http://stackoverflow.com/questions/2380073/\
    how-to-identify-what-function-call-raise-an-exception-in-python
    """
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][3]
    return fname


def log_exception(e):
    logger.error(
        "Function {function_name} raised {exception_class} ({exception_docstring}): {exception_message} at {linenumber}".format(
            function_name=extract_function_name(),  # this is optional
            exception_class=e.__class__,
            exception_docstring=e.__doc__,
            exception_message=e.message, linenumber=traceback.tb_lineno(sys.exc_info()[-1])))


def log_setup(config, level='WARN', stdout=False):

    log_file = config['log_file']

    lvls = {'CRITICAL': 50,
            'ERROR': 40,
            'WARNING': 30,
            'INFO': 20,
            'DEBUG': 10}

    lvl = lvls[level]

    if level == 'DEBUG' or stdout:
        logformat = '[%(asctime)s] [%(threadName)s] [%(levelname)s] [%(module)s] [%(lineno)d] [%(name)s] : %(message)s'

    else:
        logformat = '[%(asctime)s] [%(levelname)s] : %(message)s'

    formatter = logging.Formatter(logformat)

    try:
        if stdout:
            logger.setLevel(logging.DEBUG)
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(formatter)
            streamHandler.setLevel(logging.DEBUG)
            logger.addHandler(streamHandler)

        else:
            logging.basicConfig(
                filename=log_file, level=lvl, format=logformat)

    except Exception as e:
        log_exception(e)


class Elements(object):

    def __init__(self, hostname, element_obj):
        self.hostname = hostname
        self.element = element_obj
        self.elements = {}
        self.elements[self.hostname] = self.element

    def add(self, metricId, ts, val, metricType, sign=None, rate=None, tags=[], elementId=None):
        logger.debug('Element.add for metricId: {0}, ts: {1}, val: {2}, metricType:{3}, sign: {4}, rate: {5}, tags: {6}, elementId: {7}'.format(
            str(metricId), str(ts), str(val), str(metricType), str(sign),
            str(rate), str(tags), str(elementId)))

        try:
            timestamp = int(ts)
            value = val

            for t in tags:
                if 'elementid' in t:
                    elementId = t['elementid']

            if elementId is None:
                elementId = self.hostname

            if elementId not in self.elements:
                self.elements[elementId] = Element(elementId)

            self.elements[elementId].add_sample(
                metricId, timestamp, value, metricType, sign, rate, tags)

        except Exception as e:
            log_exception(e)

    def delete(self, elementId):
        del self.elements[elementId]

    def clear_samples(self, elementId=None, everything=False):
        logger.debug('Element.clear_samples for ' + str(elementId))
        try:
            if elementId is None and everything is True:
                for ename in self.elements:
                    e = self.elements[ename]
                    e.clear_samples()

            else:
                e = self.elements[elementId]
                e.clear_samples()

        except Exception as e:
            log_exception(e)


class Poster(threading.Thread):

    """
    Thread for posting the collected data to Netuitive's API
    """

    def __init__(self, config, element):
        logger.debug('Poster')
        threading.Thread.__init__(self)
        self.setName('PosterThread')
        self.lock = threading.Lock()
        self.config = config
        self.runner = threading.Event()
        self.sample_count = float(0)
        self.packet_count = float(0)
        self.event_count = float(0)
        self.metric_prefix = self.config['prefix']
        self.stats_prefix = self.metric_prefix + '.netuitive-statsd'

        logger.info('Messages will be sent to ' + self.config['url'])

        self.api = netuitive.Client(self.config['url'], self.config['api_key'])
        self.interval = self.config['interval']
        self.hostname = config['hostname']
        self.events = []
        self.elements = Elements(self.hostname, element)

    def stop(self):
        logger.info("Shutting down")
        self.runner.set()

    def run(self):
        while not self.runner.is_set():
            logger.debug('Waiting {0} seconds'.format(self.interval))
            self.runner.wait(self.interval)
            logger.debug('Flushing')
            self.flush()

    def flush(self):
        try:
            with self.lock:
                timestamp = int(time.time())

                # add some of our metric samples
                self.elements.add(self.stats_prefix + '.packets_received.count',
                                  timestamp,
                                  self.packet_count,
                                  'c')

                self.elements.add(self.stats_prefix + '.samples_received.count',
                                  timestamp,
                                  self.sample_count,
                                  'c')

                self.elements.add(self.stats_prefix + '.event_received.count',
                                  timestamp,
                                  self.event_count,
                                  'c')

                logger.debug('Sample count: {0}'.format(self.sample_count))
                logger.debug('Packet count: {0}'.format(self.packet_count))
                logger.debug('Event count: {0}'.format(self.event_count))

                ec = 0
                sc = 0

                logger.debug(
                    'Flushing {0} elements with {1} samples total'.format(ec, sc))

                for ename in self.elements.elements:
                    e = self.elements.elements[ename]
                    e.prepare()
                    element = e.element
                    ec += 1
                    sc += len(element.samples)

                    logger.debug(
                        '{0} has {1} samples'.format(ename, len(element.samples)))
                    for s in element.samples:
                        logger.debug('elementId: {0} metricId: {1} value: {2} timestamp: {3}'.format(
                            ename, s.metricId, s.val, str(s.timestamp)))

                    if sc > 0:
                        logger.debug(
                            'sending {0} samples for for {1}'.format(sc, ename))

                        if self.api.post(element):
                            logger.info(
                                'Successfully sent {0} elements with {1} samples total'.format(ec, sc))

                            self.elements.clear_samples(ename)

                        else:
                            logger.warn(
                                'Failed to send {0} elements with {1} samples total'.format(ec, sc))

                logger.debug(
                    'Flushing {0} events'.format(len(self.events)))

                for event in self.events:

                    if self.api.post_event(event):
                        logger.info(
                            'Successfully sent event titled {0}'.format(event.title))

                    else:
                        logger.warn(
                            'Failed to send {0} event titled {0}'.format(event.title))

                # reset
                self.sample_count = float(0)
                self.packet_count = float(0)
                self.event_count = float(0)
                self.events = []

        except Exception as e:
            log_exception(e)

    def submit(self, message, ts):

        timestamp = int(ts)

        try:

            self.packet_count += 1

            messages = parse_message(message)

            if messages is not None:
                self.sample_count += float(messages['counts']['messages'])
                self.event_count += float(messages['counts']['events'])

                if len(messages['events']) > 0:

                    for e in messages['events']:

                        title = e['title']
                        text = e['text']
                        tgs = e['tags']
                        tags = []

                        for t in tgs:
                            for k, v in t.iteritems():
                                tags.append((k, v))

                        if e['hostname'] is None:
                            eid = self.hostname
                        else:
                            eid = e['hostname']

                        if e['priority'] is not None:
                            lvl = e['priority']
                        else:
                            lvl = 'INFO'

                        if e['date_happened'] is not None:
                            tags.append(
                                ('date_happened', e['date_happened']))

                        if e['aggregation_key'] is not None:
                            tags.append(
                                ('aggregation_key', e['aggregation_key']))

                        if e['source_type_name'] is not None:
                            tags.append(
                                ('source_type_name', e['source_type_name']))

                        if e['alert_type'] is not None:
                            tags.append(('alert_type', e['alert_type']))

                        with self.lock:
                            self.events.append(netuitive.Event(eid, 'INFO', title, text, lvl, tags, timestamp,
                                                               'netuitive-statsd'))

                if len(messages['metrics']) > 0:
                    for m in messages['metrics']:
                        with self.lock:
                            self.elements.add(
                                self.metric_prefix + '.' + m['name'],
                                timestamp,
                                m['value'],
                                m['type'],
                                m['sign'],
                                m['rate'],
                                m['tags']
                            )

        except Exception as e:
            print(e)
            log_exception(e)
            raise(e)


class Server(object):

    """
    StatsD server
    """

    def __init__(self, config, poster):
        self.config = config
        self.poster = poster
        self.listen_ip = self.config['listen_ip']
        self.listen_port = int(self.config['listen_port'])
        self.prefix = self.config['prefix']
        self.address = (self.listen_ip, self.listen_port)
        self.hostname = config['hostname']
        self.buffer_size = 8192
        self.is_running = False
        self.forward = self.config['forward']

        # if enabled, setup StatsD forwarding
        if self.forward is True:
            self.forward_ip = self.config['forward_ip']
            self.forward_port = int(self.config['forward_port'])

            logger.info("All packets received will be forwarded to {0}:{1}".format(
                self.forward_ip, self.forward_port))
            try:
                self.forward_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)
                self.forward_sock.connect(
                    (self.forward_ip, self.forward_port))
            except Exception as e:
                logger.exception(
                    "Error while setting up connection to external statsd server: {0}".format(str(e)))
                log_exception(e)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        try:
            self.socket.bind(self.address)
        except socket.gaierror:
            if self.address[0] == 'localhost':
                self.address = ('127.0.0.1', self.address[1])
                self.socket.bind(self.address)

        logger.info('Listening on {0}:{1}'.format(
            self.address[0], self.address[1]))

        # Run loop
        self.is_running = True

        while self.is_running:
            try:
                ready = select.select([self.socket], [], [], 5)

                if ready[0]:
                    # get the packet
                    packet = self.socket.recv(self.buffer_size)
                    timestamp = time.time()
                    logger.debug('Received packer: ' + packet.rstrip('\n'))
                    self.poster.submit(packet, timestamp)

                    if self.forward is True:
                        logger.debug('Forwarded packet: ' + packet)
                        self.forward_sock.send(packet)

            except select.error as e:
                errno = e[0]
                if errno != 4:
                    raise

            except (KeyboardInterrupt, SystemExit):
                self.poster.stop()
                break

            except Exception as e:
                log_exception(e)

    def stop(self):
        logger.info("Shutting down")
        self.is_running = False


class Service(Daemon):

    """
    Daemon management
    """

    def __init__(self, config, server, poster):
        self.config = config
        self.pid_file = self.config['pid_file']
        Daemon.__init__(self, self.pid_file)
        self.server = server
        self.poster = poster

    def _handle_sigterm(self, signum, frame):
        logger.debug('Sigterm. Stopping.')
        self.server.stop()
        self.poster.stop()

    def run(self):
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigterm)
        self.poster.start()

        try:
            try:
                self.server.start()

            except Exception as e:
                logger.exception('Error starting server')
                raise e
        finally:
            self.poster.stop()
            self.poster.join()
            logger.info("Stopped")


if __name__ == "__main__":

    try:
        # set the process name for ps
        setproctitle(
            os.path.realpath(__file__) + ' ' + ' '.join(sys.argv[1:]))

        # Initialize Config
        args = docopt(__doc__, version=__version__)
        configfile = os.path.abspath(args['--configfile'])

        # try to load the agent config
        if os.path.exists(configfile):
            config = configobj.ConfigObj(configfile)
        else:
            print >> sys.stderr, 'ERROR: Config file: {0} does not exist.'.format(
                configfile)
            sys.exit(1)

        if args['--debug']:
            CONFIG['debug'] = True

        # Defaults
        CONFIG['interval'] = 60
        CONFIG['element_type'] = "SERVER"
        CONFIG['prefix'] = "statsd"
        CONFIG['listen_port'] = 8125
        CONFIG['listen_ip'] = '127.0.0.1'
        CONFIG['forward_port'] = None
        CONFIG['forward_ip'] = None
        CONFIG['forward'] = False

        # assemble the diamond.conf config
        CONFIG['configfile'] = configfile
        CONFIG['url'] = config['handlers']['NetuitiveHandler']['url']
        CONFIG['api_key'] = config['handlers'][
            'NetuitiveHandler']['api_key']

        if 'statsd' in config['handlers']['NetuitiveHandler']:
            s = config['handlers']['NetuitiveHandler']['statsd']

            if 'element_type' in s:
                CONFIG['element_type'] = s['element_type']

            if 'prefix' in s:
                CONFIG['prefix'] = s['prefix']

            if 'listen_ip' in s:
                CONFIG['listen_ip'] = s['listen_ip']

            if 'listen_port' in s:
                CONFIG['listen_port'] = s['listen_port']

            if 'forward_ip' in s:
                CONFIG['forward_ip'] = s['forward_ip']

            if 'forward_port' in s:
                CONFIG['forward_port'] = s['forward_port']

            if 'forward' in s:
                CONFIG['forward'] = s['forward']

            if 'interval' in s:
                CONFIG['interval'] = int(s['interval'])

        CONFIG['pid_file'] = os.path.dirname(
            config['server']['pid_file']) + '/netuitive-statsd.pid'

        log_file = os.path.dirname(
            config['handler_rotated_file']['args'][0].split("'")[1]) + '/netuitive-statsd.log'

        CONFIG['log_file'] = log_file

        if 'hostname' in config['collectors']['default']:
            CONFIG['hostname'] = config[
                'collectors']['default']['hostname']

        loglvl = config['logger_root']['level']

        # setup logging
        log_setup(CONFIG, loglvl, stdout=CONFIG['debug'])
        logger.info('Loaded config from ' + configfile)

        # create and element and add metadata
        myElement = Element(CONFIG['hostname'])

        # setup Netuitive API posting thread
        poster = Poster(CONFIG, myElement)

        # setup StatsD server
        server = Server(CONFIG, poster)

        # do my job
        if CONFIG['debug'] is False:
            daemon = Service(CONFIG, server, poster)

            if args['<command>'] == 'start':
                daemon.start()

            elif args['<command>'] == 'stop':
                daemon.stop()

            elif args['<command>'] == 'restart':
                daemon.restart()

            elif args['<command>'] == 'info':
                print(json.dumps(CONFIG, indent=2, sort_keys=True))
                print(sys.argv[1:])

        else:
            # do my job loudly!
            logger.debug('debug logging is on')
            poster.start()
            server.start()

    except Exception as e:
        log_exception(e)
