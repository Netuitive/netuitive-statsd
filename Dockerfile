FROM python:2.7-onbuild

ENV APIKEY apikey
ENV APIURL "https://api.app.netuitive.com/ingest"
ENV INTERVAL 60
ENV ELEMENTTYPE SERVER
ENV PREFIX statsd
ENV DOCKER_HOSTNAME ${HOSTNAME}
ENV LIP "0.0.0.0"
ENV LPRT 8125
ENV FIP "127.0.0.1"
ENV FPRT 8125
ENV FORWARD ""
ENV DEBUG ""


ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /opt/netuitive-statsd
COPY . /opt/netuitive-statsd

WORKDIR /opt/netuitive/netuitive-statsd

EXPOSE 8125/udp


ENTRYPOINT ["/entrypoint.sh"]
