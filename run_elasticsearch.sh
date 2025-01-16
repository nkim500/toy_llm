#!/bin/bash

docker run -d --name es \
	-p 127.0.0.1:9200:9200 \
	-e "discovery.type=single-node" \
	-e "xpack.security.enabled=false" \ 
	docker.elastic.co/elasticsearch/elasticsearch:8.6.0
