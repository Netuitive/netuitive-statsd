Netuitive StatsD Server Usage
=============================



Config file
-----------
While the intended use case for this server is to be part of the [Netuitive Linux Agent distribution](https://github.com/Netuitive/omnibus-netuitive-agent), netuitive-statsd can be run stand-alone.

See [netuitive-statsd.conf.example](netuitive-statsd.conf.example) as an example

Command-line Usage
------------------

    Usage:
            netuitive-statsd [-d] [-f] -c <CONFIG> <command>
            netuitive-statsd [-d] [-f] --api_key=<API_KEY>
                [--url=<URL>] [--interval=<INTERVAL>] [--element_type=<TYPE>]
                [--prefix=<PREFIX>] [--hostname=<HOSTNAME>] [--pid_file=<PID>]
                [--log_file=<LOG>] [--listen_ip=<LIP>] [--listen_port=<LPRT>]
                [--forward_ip=<FIP>] [--forward_port=<FPRT>] [--forward]
                [--log_level=<LEVEL>] [--nolog]
                <command>

             <command>
            netuitive-statsd -h | --help
            netuitive-statsd --version

    Description:
            Netuitive StatsD server

    Examples:
            netuitive-statsd -c ./netuitive-statsd.conf start
            netuitive-statsd stop
            netuitive-statsd restart


    Options:
        -c CONFIG --configfile=CONFIG    Config file
        --api_key=API_KEY      API key
        --pid_file=PID         Process ID (PID) file to use [default: ./netuitive-statsd.pid]
        --log_file=LOG         Log file to use [default: ./netuitive-statsd.log]
        --log_level=LEVEL      Log level [default: WARNING]
        --nolog                Disable writing to the log file
        --url=URL              API URL [default: https://api.app.netuitive.com/ingest]
        --hostname=HOSTNAME    Hostname (Element ID)
        --interval=INTERVAL    Interval to send messages [default: 60]
        --element_type=TYPE    Element Type [default: statsd]
        --prefix=PREFIX        Metrics prefix [default: statsd]
        --listen_ip=LIP        IP address to listen on [default: 127.0.0.1]
        --listen_port=LPRT     UDP port to listen on [default: 8125]
        --forward_ip=FIP       IP address to forward StatsD messages to
        --forward_port=FPRT    UDP port to forward  StatsD messages to [default: 8125]
        --forward              Enable StatsD forwarding

        -d --debug             Enable debug output
        -f --foreground        Enable foreground for console logging


        -h --help     Show this screen.
        --version     Show version.
    Docker Build
    ------------
        docker build --rm=true -t netuitive/netuitive-statsd .

Docker Usage
------------
    docker run -d -p 8125:8125/udp -e DOCKER_HOSTNAME=my-docker-host -e APIKEY=my-api-key --name netuitive-statsd netuitive/netuitive-statsd

See the [Dockerfile](Dockerfile) for more environment variables that can be used.

Sending StatsD metrics
----------------------
Configure you application or your Application's StatsD library of choice to send to `localhost:8125`.


Sending DogStatsd Metrics / Events
----------------------
Configure your Application's DogStatsD library of choice to send to `localhost:8125`.

Reserved Metric Tags
--------------------
| Tag  | Meaning  |
| ---- | -------- |
| h | hostname (elementId)  |
| un | sets the unit of the metric (bits, bytes, etc) |
| sds | sets the sparse data strategy (ReplaceWithZero, etc) |


Copyright and License
---------------------

Copyright 2016 Netuitive, Inc. under [the Apache 2.0 license](LICENSE).
