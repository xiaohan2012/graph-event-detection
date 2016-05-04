#! /bin/bash

timeout 5h python twitter_stream_listener.py \
	--terms  mcfc mancity realmadrid realmadriden \
    --mongo_col madrid_mancity_1
