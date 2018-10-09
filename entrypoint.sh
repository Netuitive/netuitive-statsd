#!/bin/bash
set -e

fwd=""

if [ -n "${FORWARD}" ]; then
    fwd="--forward"
fi

if [ -n "${DEBUG}" ]; then
    debug="-d"
fi


python /opt/netuitive-statsd/netuitive-statsd \
--nolog \
--api_key=${APIKEY} \
--url=${APIURL} \
--hostname=${DOCKER_HOSTNAME} \
--interval=${INTERVAL} \
--element_type=${ELEMENTTYPE} \
--prefix=${PREFIX} \
--listen_ip=${LIP} \
--listen_port=${LPRT} \
--forward_ip=${FIP} \
--forward_port=${FPRT} \
${fwd} \
${debug} \
start -f
