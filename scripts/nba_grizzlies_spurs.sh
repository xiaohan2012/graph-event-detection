#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms spurs gospursgo \
	memgrizz grizz grizzlies \
    --mongo_col grizz_spurs
