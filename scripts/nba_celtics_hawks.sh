#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms celtics hawks \
    --mongo_col celtics_hawks
