#!/bin/sh

sleep 2

while [ 1 ]; do

nohup echo "format fail|sk" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "counter:1|c" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "lotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c\nlotsofcounters:1|c" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "counter.rate:1|c|@0.1" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "timer:320|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer.rate:320|ms|@0.1" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "timer2:100|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:10|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:100|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:10|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:100|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:10|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:100|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:10|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:100|ms" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "timer2:10|ms" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "gauge:333|g" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "gauge.negative:-10|g" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "gauge.positive:+4|g" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "gauge.signed:10|g" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "gauge.signed:+10|g" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "gauge.signed:-5|g" | nc -w 1 -u 127.0.0.1 8125 &


nohup echo "set1:1|s" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "set1:1|s" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "set1:1|s" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "set2:1|s" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "set2:2|s" | nc -w 1 -u 127.0.0.1 8125 &
nohup echo "set10:1|s\nset10:2|s\nset10:3|s\nset10:4|s\nset10:5|s\nset10:6|s\nset10:7|s\nset10:8|s\nset10:9|s\nset10:10|s" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "host2.counter:1|c|#host:statsdhosttag01" | nc -w 1 -u 127.0.0.1 8125 &

nohup echo "everything.counter:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.lotsofcounters:1|c\neverything.counter2:1|c|#host:host2\neverything.counter.rate:1|c|@0.1\neverything.timer:320|ms\neverything.timer.rate:320|ms|@0.1\neverything.timer2:100|ms\neverything.timer2:10|ms\neverything.timer2:100|ms\neverything.timer2:10|ms\neverything.timer2:100|ms\neverything.timer2:10|ms\neverything.timer2:100|ms\neverything.timer2:10|ms\neverything.timer2:100|ms\neverything.timer2:10|ms\neverything.gauge:333|g\neverything.gauge.negative:-10|g\neverything.gauge.positive:+4|g\neverything.gauge.signed:10|g\neverything.gauge.signed:+10|g\neverything.gauge.signed:-5|g\neverything.set1:1|s\neverything.set1:1|s\neverything.set1:1|s\neverything.set2:1|s\neverything.set2:2|s\neverything.set10:1|s\neverything.set10:2|s\neverything.set10:3|s\neverything.set10:4|s\neverything.set10:5|s\neverything.set10:6|s\neverything.set10:7|s\neverything.set10:8|s\neverything.set10:9|s\neverything.set10:10|s" | nc -w 1 -u 127.0.0.1 8125



# nohup echo "_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3" | nc -w 1 -u 127.0.0.1 8125


sleep 6

done



