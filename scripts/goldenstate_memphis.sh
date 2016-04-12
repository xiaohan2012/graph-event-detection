#! /bin/bash

python twitter_stream_listener.py \
	--terms goldenstate warriors stephencurry \
	memgrizz grizz grizzlies\
	nba nbaplayoffs \
    --mongo_col test
