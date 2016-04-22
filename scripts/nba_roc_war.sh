#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms houston rockets goldenstate warriors \
    --mongo_col roc_war
