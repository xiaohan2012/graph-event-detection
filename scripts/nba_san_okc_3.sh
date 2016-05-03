#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms okcthunder thunder spurs san antonio \
    --mongo_col san_okc_3
