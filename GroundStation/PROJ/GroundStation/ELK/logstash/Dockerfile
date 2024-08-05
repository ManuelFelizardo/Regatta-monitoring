# https://github.com/elastic/logstash-docker
FROM docker.elastic.co/logstash/logstash-oss:6.2.3

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json

RUN logstash-plugin install logstash-input-udp
RUN logstash-plugin install logstash-output-influxdb
RUN logstash-plugin update logstash-input-udp
RUN logstash-plugin update logstash-output-influxdb
