FROM python:2

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /opt/netuitive/netuitive-statsd
COPY . /opt/netuitive/netuitive-statsd

RUN mkdir -p /etc/netuitive/netuitive-statsd
COPY netuitive-agent.conf /etc/netuitive/netuitive-statsd/netuitive-agent.conf

WORKDIR /opt/netuitive/netuitive-statsd
RUN cat get-pip.py | python
RUN pip install -r requirements.txt
RUN pip install --upgrade netuitive

EXPOSE 8125

CMD ["/usr/bin/supervisord"]
