#! /bin/bash

python draw_events_in_original_people_network.py \
	-m tmp/beefban/meta-graph*hashtag*.pkl \
	-r tmp/beefban/result-greedy--U=15.0--dijkstra=False--timespan=1*.pkl \
	-k 5 \
	-o /cs/home/hxiao/public_html/figures/events_vs_people_network.png


chmod a+r /cs/home/hxiao/public_html/figures/events_vs_people_network.png
