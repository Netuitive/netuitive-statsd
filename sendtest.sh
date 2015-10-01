#!/bin/sh

sleep 2

while [ 1 ]; do

# echo "format fail|sk" | nc -w 1 -u 127.0.0.1 8125
echo "counter:1|c" | nc -w 1 -u 127.0.0.1 8125
echo "counter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c\ncounter:1|c" | nc -w 1 -u 127.0.0.1 8125

#echo "counter2:1|c|#host:host2" | nc -w 1 -u 127.0.0.1 8125

# echo "counter.rate:1|c|@0.1" | nc -w 1 -u 127.0.0.1 8125
# echo "timer:320|ms" | nc -w 1 -u 127.0.0.1 8125
# echo "timer.rate:320|ms|@0.1" | nc -w 1 -u 127.0.0.1 8125
# echo "gauge:333|g" | nc -w 1 -u 127.0.0.1 8125
# echo "gauge.negative:-10|g" | nc -w 1 -u 127.0.0.1 8125
# echo "gauge.positive:+4|g" | nc -w 1 -u 127.0.0.1 8125
# echo "set:123|s" | nc -w 1 -u 127.0.0.1 8125
# echo "set:456|s\nset:456|s\nset:456|s\nset:456|s\nset:456|s\nset:456|s\nset:456|s\nset:456|s\nset:456|s\nset:456|s" | nc -w 1 -u 127.0.0.1 8125

# echo "counter:1|c\nratecounter:1|c|@0.1\ntimer:320|ms\ratetimer:320|ms|@0.1\ngauge:333|g\nnegativegauge:-10|g\npositivegauge:+4|g\nset:789|s" | nc -w 1 -u 127.0.0.1 8125
# echo "_e{5,4}:title|text|d:date_happened|h:hostname|k:aggregation_key|p:priority|s:source_type_name|t:alert_type|#tag1,tag2,tag3:value3" | nc -w 1 -u 127.0.0.1 8125


sleep 1

done



