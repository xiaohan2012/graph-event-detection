paths=("result-greedy--U=0.5--dijkstra=False--timespan=28days----dist_func=cosine.pkl"	"result-greedy--U=0.5--dijkstra=False--timespan=28days----dist_func=euclidean.pkl"	"result-lst--U=0.5--dijkstra=False--timespan=28days----dist_func=cosine.pkl"	"result-lst--U=0.5--dijkstra=False--timespan=28days----dist_func=euclidean.pkl"	"result-lst--U=0.5--dijkstra=True--timespan=28days----dist_func=cosine.pkl"	"result-lst--U=0.5--dijkstra=True--timespan=28days----dist_func=euclidean.pkl"	"result-random--U=0.5--dijkstra=False--timespan=28days----dist_func=cosine.pkl"	"result-random--U=0.5--dijkstra=False--timespan=28days----dist_func=euclidean.pkl")

for p in "${paths[@]}"
do
	echo $p
	python event_graph_structure.py tmp/$p
done
