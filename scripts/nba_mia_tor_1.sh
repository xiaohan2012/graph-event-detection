#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms  miami heat toronto raptors \
    --mongo_col mia_tor_1
