#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms  atlhawks atlanta hawks cavs cleveland cavaliers \
    --mongo_col atl_cel_2
