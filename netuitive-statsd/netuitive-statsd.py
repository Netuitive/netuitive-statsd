#!/bin/env python2.7
# --*-- Encoding: UTF-8 --*--
"""Usage:
        netuitive_statsd [-d] -c CONFIG [-p PORT] [-i IP] [(--fip FORWARDIP --fport FORWARDPORT)] [--type TYPE] <command>

        netuitive_statsd -h | --help
        netuitive_statsd --version

Description:
        Netuitive StatsD server

Examples:
        examples would be awesome
Options:
    -c CONFIG --configfile=CONFIG    Config file
    -p PORT --port=PORT    Port to listen on [default: 8125]
    -i IP --ip=IP    IP to listen on [default: 127.0.0.1]
    --fip=FORWARDIP       IP to forward to
    --fport=FORWARDPORT     Port to forward to
    --type=TYPE    Set Element type [default: SERVER]
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
from daemon import Daemon
from setproctitle import setproctitle
import netuitive
from elements import Element

# Constants
__version__ = "0.0.1"
__author__ = "Netuitive, Inc."
__license__ = "Apache 2.0"

logger = logging.getLogger()


REGEX = re.compile(
    r'((?P<metric_name>[a-zA-Z0-9\.]+):(?P<metric_sign>[-\+])?(?P<metric_value>[\d\-\+]+)\|(?P<metric_type>[\w]+)(\|@(?P<metric_rate>[\d\.]+))?(\|#(?P<metric_tags>[\w:,]+))?(\\n)?)?(^_e{(?P<event_title_length>[\d]+),(?P<event_text_length>[\d]+)}:(?P<event_title>[^|]+)\|(?P<event_text>[^|\n]+)?(\|d:(?P<event_date_happened>[^|\n]+))?(\|h:(?P<event_hostname>[^|\n]+))?(\|k:(?P<event_aggregationkey>[^|\n]+))?(\|p:(?P<event_priority>[^|\n]+))?(\|s:(?P<event_source_type_name>[^|\n]+))?(\|t:(?P<event_alert_type>[^|\n]+))?(\|#(?P<event_tags>[\w\d,:]+))?$)?')


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


def get_human_readable_size(num):
    """
    return the human readable form of num (bytes)
    """
    exp_str = [(0, 'B'), (10, 'KB'), (20, 'MB'),
               (30, 'GB'), (40, 'TB'), (50, 'PB'), ]
    i = 0
    while i + 1 < len(exp_str) and num >= (2 ** exp_str[i + 1][0]):
        i += 1
        rounded_val = round(int(num) / 2 ** exp_str[i][0], 2)
    return '%s %s' % (int(rounded_val), exp_str[i][1])


def check_lsb():
    """
    if we can find it, return the linux distribution info
    """
    if os.path.isfile("/etc/lsb-release"):
        try:
            _distributor_id_file_re = re.compile(
                "(?:DISTRIB_ID\s*=)\s*(.*)", re.I)
            _release_file_re = re.compile(
                "(?:DISTRIB_RELEASE\s*=)\s*(.*)", re.I)
            _codename_file_re = re.compile(
                "(?:DISTRIB_CODENAME\s*=)\s*(.*)", re.I)
            with open("/etc/lsb-release", "rU") as etclsbrel:
                for line in etclsbrel:
                    m = _distributor_id_file_re.search(line)
                    if m:
                        _u_distname = m.group(1).strip()
                    m = _release_file_re.search(line)
                    if m:
                        _u_version = m.group(1).strip()
                    m = _codename_file_re.search(line)
                    if m:
                        _u_id = m.group(1).strip()
                if _u_distname and _u_version:
                    return (_u_distname, _u_version, _u_id)

        except Exception as e:
            log_exception(e)
            return(None)

    else:
        return(None)


def get_sys_meta():
    """
    return some system metadata
    """
    ret = []
    try:

        ret.append({'platform': platform.system()})

        if psutil:
            ret.append({'cpus': psutil.cpu_count()})

            mem = psutil.virtual_memory()
            ret.append({'ram': get_human_readable_size(mem.total)})
            ret.append({'ram bytes': mem.total})
            ret.append(
                {'boottime': str(datetime.datetime.fromtimestamp(psutil.boot_time()))})

        if platform.system().startswith('Linux'):
            if check_lsb() is None:
                supported_dists = platform._supported_dists + ('system',)
                dist = platform.linux_distribution(
                    supported_dists=supported_dists)

            else:
                dist = check_lsb()

            ret.append({'distribution_name': str(dist[0])})
            ret.append({'distribution_version': str(dist[1])})
            ret.append({'distribution_id': str(dist[2])})

        ret.append({'netuitive-statsd': __version__})

        logger.info('Added system metadata')

    except Exception as e:
        log_exception(e)

    return(ret)


def get_docker_meta():
    """
    if we can find it, return some docker metadata
    """
    ret = []

    if docker:
        try:
            if os.path.isfile('/var/run/docker.sock'):
                cc = docker.Client(
                    base_url='unix://var/run/docker.sock', version='auto')
                dockerver = cc.version()

                for k, v in dockerver.items():
                    if type(v) is list:
                        vl = ', '.join(v)
                        v = vl
                    ret.append({'docker_' + k: v})

            logger.info('Added docker metadata')

        except Exception:
            pass

    return(ret)


def get_aws_meta():
    """
    if we can find it, return some aws metadata
    """
    ret = []
    url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'

    try:
        request = urllib2.Request(url)
        resp = urllib2.urlopen(request, timeout=1).read()
        j = json.loads(resp)

        for k, v in j.items():
            if type(v) is list:
                vl = ', '.join(v)
                v = vl
            ret.append({k: v})
        logger.info('Added AWS metadata')

    except Exception as e:
        if CONFIG['debug'] is True:
            log_exception(e)

    return(ret)


def add_metadata(element, tags):
    """
    gather metadata and add it to the element as attributes and tags
    """
    try:

        logger.info('Gathering metadata')

        for a in get_sys_meta():
            for k in a:
                element.add_attribute(k, a[k])

        for a in get_docker_meta():
            for k in a:
                element.add_attribute(k, a[k])

        for a in get_aws_meta():
            for k in a:
                element.add_attribute(k, a[k])

        if tags is not None:
            if type(tags) is list:
                for k, v in dict(tag.split(":") for tag in tags).iteritems():
                    element.add_tag(k.strip(), v.strip())

            if type(tags) is str:
                element.add_tag(tags.split(":")[0], tags.split(":")[1])

    except Exception as e:
        log_exception(e)


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


def regex_parse_message(message):
    """
    parse a statsd message via regex and return the results
    """
    ret = {}
    ret['metrics'] = []
    ret['events'] = []

    sample_count = 0
    event_count = 0

    try:
        for msg in re.finditer(REGEX, message):
            if msg.group(0):
                sample_count += 1
                if msg.group('metric_name'):
                    rate = None
                    sign = None
                    tags = []

                    metric = msg.group('metric_name')
                    value = float(msg.group('metric_value'))
                    mtype = msg.group('metric_type')

                    if msg.group('metric_rate'):
                        rate = float(msg.group('metric_rate'))

                    if msg.group('metric_sign'):
                        sign = msg.group('metric_sign')

                    if msg.group('metric_tags'):
                        tgs = msg.group('metric_tags')

                        for ts in tgs.split(','):
                            t = ts.split(':')
                            if len(t) == 2:
                                tags.append({t[0]: t[1]})
                            else:
                                tags.append({t[0]: None})

                    logger.debug(
                        'Message (metric): ' + str((metric, value, mtype, sign, rate, tags)))

                    ret['metrics'].append({
                        'metric': metric,
                        'value': value,
                        'type': mtype,
                        'sign': sign,
                        'rate': rate,
                        'tags': tags})

                elif msg.group('event_title'):

                    date_happened = ''
                    hostname = ''
                    aggregationkey = ''
                    priority = ''
                    source_type_name = ''
                    alert_type = ''
                    tags = []
                    event_count += 1

                    title = msg.group('event_title')
                    text = msg.group('event_text')

                    if msg.group('event_date_happened'):
                        date_happened = msg.group('event_date_happened')

                    if msg.group('event_hostname'):
                        hostname = msg.group('event_hostname')

                    if msg.group('event_aggregationkey'):
                        aggregation_key = msg.group('event_aggregationkey')

                    if msg.group('event_priority'):
                        priority = msg.group('event_priority')

                    if msg.group('event_source_type_name'):
                        source_type_name = msg.group('event_source_type_name')

                    if msg.group('event_alert_type'):
                        alert_type = msg.group('event_alert_type')

                    if msg.group('event_tags'):
                        tgs = msg.group('event_tags')

                        for ts in tgs.split(','):
                            t = ts.split(':')
                            if len(t) == 2:
                                tags.append({t[0]: t[1]})
                            else:
                                tags.append({t[0]: None})

                    logger.debug(
                        'Message (event): ' + str((title, text, date_happened, hostname, aggregation_key, priority, source_type_name, alert_type, tags)))

                    ret['events'].append({
                        'title': title,
                        'text': text,
                        'date_happened': date_happened,
                        'hostname': hostname,
                        'aggregation_key': aggregationkey,
                        'priority': priority,
                        'source_type_name': source_type_name,
                        'alert_type': alert_type,
                        'tags': tags})

        if sample_count == 0:
            logger.error(
                'Invalid Message Format: "' + str(message) + '"')
            return(None)

        ret['counts'] = {'messages': sample_count, 'events': event_count}

        return(ret)

    except Exception as e:
        log_exception(e)


# def parse_message(message):
#     """
#     parse a statsd message via string splitting and return the results
#     """
#     ret = {}
#     ret['metrics'] = []
#     ret['events'] = []

#     sample_count = 0
#     event_count = 0

#     try:
#         for msg in message.splitlines():

#             parts = msg.split('|')
#             if parts[0].startswith('_e'):
#                 sample_count += 1
#                 date_happened = ''
#                 hostname = ''
#                 aggregationkey = ''
#                 priority = ''
#                 source_type_name = ''
#                 alert_type = ''
#                 tags = []
#                 event_count += 1

#                 title = parts[0].split(':')[1]
#                 text = parts[1]

#                 if len(parts) > 2:
#                     for p in parts[2:]:
# if p.startswith('#'):
# tgs = p.replace('#', '')
#                             for ts in tgs.split(','):
#                                 t = ts.split(':')
#                                 if len(t) == 2:
#                                     tags.append({t[0]: t[1]})
#                                 else:
#                                     tags.append({t[0]: None})

#                         else:
#                             m = p.split(':')

#                             if m[0] == 'd':
#                                 date_happened = m[1]

#                             elif m[0] == 'h':
#                                 hostname = m[1]

#                             elif m[0] == 'k':
#                                 aggregation_key = m[1]

#                             elif m[0] == 'p':
#                                 priority = m[1]

#                             elif m[0] == 's':
#                                 source_type_name = m[1]

#                             elif m[0] == 't':
#                                 alert_type = m[1]

#                 logger.debug(
#                     'Message (event): ' + str((title, text, date_happened, hostname, aggregation_key, priority, source_type_name, alert_type, tags)))

#                 ret['events'].append({
#                     'title': title,
#                     'text': text,
#                     'date_happened': date_happened,
#                     'hostname': hostname,
#                     'aggregation_key': aggregationkey,
#                     'priority': priority,
#                     'source_type_name': source_type_name,
#                     'alert_type': alert_type,
#                     'tags': tags})

#             elif len(parts[0].split(':')) > 1:
#                 sample_count += 1
#                 rate = ''
#                 tags = []
#                 metric = parts[0].split(':')[0]
#                 value = parts[0].split(':')[1]
#                 mtype = parts[1]

#                 if len(parts) > 2:
#                     if parts[2].startswith('@'):
#                         rate = parts[2].replace('@', '')

# if parts[2].startswith('#'):
# tgs = parts[2].replace('#', '')

#                         for ts in tgs.split(','):
#                             t = ts.split(':')
#                             if len(t) == 2:
#                                 tags.append({t[0]: t[1]})
#                             else:
#                                 tags.append({t[0]: None})

#                 if len(parts) > 3:

# if parts[3].startswith('#'):
# tgs = parts[3].replace('#', '')

#                         for ts in tgs.split(','):
#                             t = ts.split(':')
#                             if len(t) == 2:
#                                 tags.append({t[0]: t[1]})
#                             else:
#                                 tags.append({t[0]: None})

#                 logger.debug(
#                     'Message (metric): ' + str((metric, value, mtype, rate, tags)))

#                 ret['metrics'].append({
#                     'metric': metric,
#                     'value': value,
#                     'type': mtype,
#                     'rate': rate,
#                     'tags': tags})

#         if sample_count == 0:
#             ret = {}
#             logger.error(
#                 'Invalid Message Format: "' + str(message) + '"')
#             return(None)

#         ret['counts'] = {'messages': sample_count, 'events': event_count}

#         return(ret)

#     except Exception as e:
#         log_exception(e)


class Elements(object):

    def __init__(self, hostname, element_obj):
        self.hostname = hostname
        self.element = element_obj
        self.elements = {}
        self.elements[self.hostname] = self.element

    def add(self, metricId, ts, val, metricType, sign=None, rate=None, tags=[], elementId=None):
        # logger.debug('Element.add for metricId: {0}, ts: {1}, val: {2}, metricType:{3}, sign: {4}, rate: {5}, tags: {6}, elementId: {7}'.format(
        # str(metricId), str(ts), str(val), str(metricType), str(sign),
        # str(rate), str(tags), str(elementId)))

        try:
            timestamp = int(ts)
            value = val

            for t in tags:
                if 'host' in t:
                    elementId = t['host']

            if elementId is None:
                elementId = self.hostname

            if elementId not in self.elements:
                self.elements[elementId] = Element(elementId)

            self.elements[elementId].add_sample(
                metricId, timestamp, value, metricType, sign, rate)

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
        self.config = config
        self.runner = threading.Event()
        self.sample_count = float(0)
        self.packet_count = float(0)
        self.event_count = float(0)
        self.stats_prefix = 'netuitive-statsd'

        logger.info('Messages will be sent to ' + self.config['url'])

        self.api = netuitive.Client(self.config['url'], self.config['api_key'])
        self.interval = self.config['interval']
        self.hostname = config['hostname']
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
                    self.api.post(element)
                    self.elements.clear_samples(ename)

            logger.info(
                'Successfully sent {0} elements with {1} samples total'.format(ec, sc))

            # reset
            self.sample_count = float(0)
            self.packet_count = float(0)
            self.event_count = float(0)

        except Exception as e:
            log_exception(e)

    def submit(self, message, ts):

        timestamp = int(ts)

        try:
            self.packet_count += 1

            messages = regex_parse_message(message)

            if messages is not None:
                self.sample_count += float(messages['counts']['messages'])
                self.event_count += float(messages['counts']['events'])

                if len(messages['metrics']) > 0:
                    for m in messages['metrics']:
                        self.elements.add(
                            m['metric'],
                            timestamp,
                            m['value'],
                            m['type'],
                            m['sign'],
                            m['rate'],
                            m['tags']
                        )

        except Exception as e:
            log_exception(e)


class Server(object):

    """
    StatsD server
    """

    def __init__(self, config, poster):
        self.config = config
        self.poster = poster
        self.listen_ip = self.config['listen_ip']
        self.listen_port = int(self.config['listen_port'])
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

        # assemble the command line config
        CONFIG['element_type'] = args['--type']
        CONFIG['listen_port'] = args['--port']
        CONFIG['listen_ip'] = args['--ip']

        CONFIG['forward_port'] = args['--fport']
        CONFIG['forward_ip'] = args['--fip']

        if args['--fip']:
            CONFIG['forward'] = True

        if args['--debug']:
            CONFIG['debug'] = True

        # assemble the diamond.conf config
        CONFIG['configfile'] = configfile
        CONFIG['url'] = config['handlers']['NetuitiveHandler']['url']
        CONFIG['api_key'] = config['handlers'][
            'NetuitiveHandler']['api_key']
        if 'tags' in config['handlers']['NetuitiveHandler']:
            tags = config['handlers']['NetuitiveHandler']['tags']
        else:
            tags = None

        CONFIG['pid_file'] = os.path.dirname(
            config['server']['pid_file']) + '/netuitive-statsd.pid'

        log_file = os.path.dirname(
            config['handler_rotated_file']['args'][0].split("'")[1]) + '/netuitive-statsd.log'

        CONFIG['log_file'] = log_file

        if 'hostname' in config['collectors']['default']:
            CONFIG['hostname'] = config[
                'collectors']['default']['hostname']

        if 'interval' in config['collectors']['default']:
            CONFIG['interval'] = int(
                config['collectors']['default']['interval'])

        loglvl = config['logger_root']['level']

        # setup logging
        log_setup(CONFIG, loglvl, stdout=CONFIG['debug'])
        logger.info('Loaded config from ' + configfile)

        # create and element and add metadata
        myElement = Element(CONFIG['hostname'])
        add_metadata(myElement, tags)

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
                print(json.dumps(CONFIG, indent=2))
                print(sys.argv[1:])

        else:
            # do my job loudly!
            logger.debug('debug logging is on')
            poster.start()
            server.start()

    except Exception as e:
        log_exception(e)
