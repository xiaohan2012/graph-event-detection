#! /bin/bash

timeout 5h python twitter_stream_listener.py \
    --terms gswarriors warriors goldenstate portland trailblazers \
    --mongo_col por_gol_2
