from __future__ import print_function


import logging
import socket
import os
import configobj
import sys

logger = logging.getLogger(__name__)


def config(args=None):

    # default config
    ret = {
        'enabled': True,
        'url': 'https://api.app.netuitive.com/ingest',
        'api_key': None,
        'hostname': socket.getfqdn().split('.')[0],
        'interval': 60,
        'element_type': 'SERVER',
        'prefix': 'statsd',
        'listen_ip': '127.0.0.1',
        'listen_port': 8125,
        'forward_ip': None,
        'forward_port': None,
        'forward': False,
        'pid_file': 'netuitive-statsd.pid',
        'log_file': 'netuitive-statsd.log',
        'debug': False,
        'foreground': False,
        'nolog': False
    }

    if args is None:
        return(ret)

    try:
        if args['--configfile'] is not None:
            configfile = os.path.abspath(args['--configfile'])

            # try to load the config
            if os.path.exists(configfile):
                cfg = configobj.ConfigObj(configfile)
                logger.debug('Loaded config from ' + configfile)

            else:
                e = 'ERROR: Config file: {0} does not exist.'.format(
                    configfile)
                print(e, file=sys.stderr)

                raise(Exception(e))

            # assemble the config from config file

            ret['configfile'] = configfile
            ret['url'] = cfg['handlers']['NetuitiveHandler']['url']
            ret['api_key'] = cfg['handlers'][
                'NetuitiveHandler']['api_key']

            if 'statsd' in cfg['handlers']['NetuitiveHandler']:
                s = cfg['handlers']['NetuitiveHandler']['statsd']

                if 'element_type' in s:
                    ret['element_type'] = s['element_type']

                if 'prefix' in s:
                    ret['prefix'] = s['prefix']

                if 'listen_ip' in s:
                    ret['listen_ip'] = s['listen_ip']

                if 'listen_port' in s:
                    ret['listen_port'] = int(s['listen_port'])

                if 'forward_ip' in s:
                    ret['forward_ip'] = s['forward_ip']

                if 'forward_port' in s:
                    ret['forward_port'] = int(s['forward_port'])

                if 'forward' in s:
                    if s['forward'].lower() == 'true':
                        ret['forward'] = True

                    else:
                        ret['forward'] = False

                if 'interval' in s:
                    ret['interval'] = int(s['interval'])

                if 'enabled' in s:
                    if s['enabled'].lower() == 'true':
                        ret['enabled'] = True

                    else:
                        ret['enabled'] = False

            else:
                ret['enabled'] = False

            ret['pid_file'] = os.path.dirname(
                cfg['server']['pid_file']) + '/netuitive-statsd.pid'

            log_file = os.path.dirname(
                cfg['handler_rotated_file']['args'][0].split("'")[1]) +\
                '/netuitive-statsd.log'

            ret['log_file'] = log_file

            if 'collectors' in cfg:
                if 'hostname' in cfg['collectors']['default']:
                    ret['hostname'] = cfg[
                        'collectors']['default']['hostname']

            ret['log_level'] = cfg['logger_root']['level']

        else:
            # or assemble the config from cli
            ret['configfile'] = None
            ret['enabled'] = True
            ret['url'] = args['--url']
            ret['api_key'] = args['--api_key']
            ret['hostname'] = args['--hostname']
            ret['interval'] = args['--interval']
            ret['element_type'] = args['--element_type']
            ret['prefix'] = args['--prefix']
            ret['listen_ip'] = args['--listen_ip']
            ret['listen_port'] = args['--listen_port']
            ret['forward_ip'] = args['--forward_ip']
            ret['forward_port'] = args['--forward_port']
            ret['forward'] = args['--forward']
            ret['pid_file'] = args['--pid_file']
            ret['log_file'] = args['--log_file']
            ret['log_level'] = args['--log_level']

        ret['debug'] = args['--debug']
        ret['nolog'] = args['--nolog']
        ret['foreground'] = args['--foreground']

        # if we're in debug make sure we log in debug
        if ret['debug'] is True:
            ret['log_level'] = 'DEBUG'

        return(ret)

    except Exception as e:
        logger.error(e, exc_info=True)
        raise(e)