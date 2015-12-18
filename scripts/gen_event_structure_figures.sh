paths=("result-greedy--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl"	"result-greedy--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=euclidean.pkl"	"result-lst--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl"	"result-lst--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=euclidean.pkl"	"result-lst--U=0.05--dijkstra=True--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl"	"result-lst--U=0.05--dijkstra=True--timespan=56days----decompose_interactions=False--dist_func=euclidean.pkl"	"result-random--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl"	"result-random--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=euclidean.pkl")

for p in "${paths[@]}"
do
    echo $p
    python event_graph_structure.py tmp/$p
done
