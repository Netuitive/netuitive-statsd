
import logging

logger = logging.getLogger(__name__)


def parse_message(message):
    """
    parse a statsd message via string splitting and return the results
    """
    ret = {}
    ret['metrics'] = []
    ret['events'] = []

    sample_count = 0
    event_count = 0

    try:
        for msg in message.splitlines():

            parts = msg.split('|')

            # print(msg)  # debugging
            # print(parts)  # debugging

            if parts[0].startswith('_e'):
                # it's an even message
                sample_count += 1
                date_happened = None
                hostname = None
                aggregationkey = None
                priority = None
                source_type_name = None
                alert_type = None
                tags = []
                event_count += 1

                title = parts[0].split(':')[1]
                text = parts[1]

                if len(parts) > 2:
                    for p in parts[2:]:
                        if p.startswith('#'):
                            tgs = p.replace('#', '')
                            for ts in tgs.split(','):
                                t = ts.split(':')
                                if len(t) == 2:
                                    tags.append({t[0]: t[1]})
                                else:
                                    tags.append({t[0]: None})

                        else:
                            m = p.split(':')

                            if m[0] == 'd':
                                date_happened = m[1]

                            elif m[0] == 'h':
                                hostname = m[1]

                            elif m[0] == 'k':
                                aggregation_key = m[1]

                            elif m[0] == 'p':
                                priority = m[1]

                            elif m[0] == 's':
                                source_type_name = m[1]

                            elif m[0] == 't':
                                alert_type = m[1]

                logger.debug(
                    'Message (event): ' + str((title, text, date_happened, hostname, aggregation_key, priority, source_type_name, alert_type, tags)))

                ret['events'].append({
                    'title': title,
                    'text': text,
                    'date_happened': date_happened,
                    'hostname': hostname,
                    'aggregation_key': aggregation_key,
                    'priority': priority,
                    'source_type_name': source_type_name,
                    'alert_type': alert_type,
                    'tags': tags})

            elif len(parts[0].split(':')) > 1:
                # it's a metric

                sample_count += 1
                rate = None
                sign = None
                tags = []
                metric = parts[0].split(':')[0]
                v = parts[0].split(':')[1]

                mtype = parts[1]
                tags.append({'statsdType': mtype})

                if v.startswith('-'):
                    sign = '-'
                    value = float(v[1:])

                elif v.startswith('+'):
                    sign = '+'
                    value = float(v[1:])

                else:
                    value = float(v)

                if len(parts) > 2:
                    if parts[2].startswith('@'):
                        rate = float(parts[2].replace('@', ''))

                    if parts[2].startswith('#'):
                        tgs = parts[2].replace('#', '')

                        for ts in tgs.split(','):
                            t = ts.split(':')
                            if len(t) == 2:
                                tags.append({t[0]: t[1]})
                            else:
                                tags.append({t[0]: None})

                if len(parts) > 3:

                    if parts[3].startswith('#'):
                        tgs = parts[3].replace('#', '')

                        for ts in tgs.split(','):
                            t = ts.split(':')
                            if len(t) == 2:
                                tags.append({t[0]: t[1]})
                            else:
                                tags.append({t[0]: None})

                logger.debug(
                    'Message (metric): ' + str((metric, value, mtype, sign, rate, tags)))

                ret['metrics'].append({
                    'name': metric,
                    'value': value,
                    'type': mtype,
                    'sign': sign,
                    'rate': rate,
                    'tags': tags})

        if sample_count == 0:
            ret = {}
            logger.error(
                'Invalid Message Format: "' + str(message).rstrip() + '"')
            return(None)

        ret['counts'] = {'messages': sample_count, 'events': event_count}

        return(ret)

    except Exception as e:
        raise(e)
