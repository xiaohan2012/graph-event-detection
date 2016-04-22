#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms okcthunder thunder dallasmavs mavericks \
    --mongo_col thu_mav
