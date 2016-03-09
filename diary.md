# Week 1(Nov 23)

Day 1: 

- improved preprocessing
- checked the topic results
- meta graph construction(decomposing multiple-recipients node, add weight to edge, round to fixed decimal point)

Day 2:

- binarize general DAG, add reward attribute to node(as we need to create dummy nodes)
- preprocess enron.json
- test `lst` for binarized DAG
- binarized DAG back to its original form
- two bugs found in `lst_dag`: 1, attr not copying 2, assign solution even if `max_nodes` is None

Day 3:

- test `get_rooted_subgraph_within_timespan`
- remove duplicate recipients(some nodes don't have `datetime`)

Day 4:

- functional test for subset of `enron.json`
- Write the algorithm that gets A_u[i] for all nodes
- maximum coverage algorithm

Day 5:

- Pickling graph is slow. Tried to convert node label to integer but still slow. 
- some bench mark: 30 mins for 500 nodes(find the best tree process)
- Check overlap in the final events(no overlap)
- Q: what do events with highest score look like? what are the top K events?

# Week 2

Day 1: 

- histogram(#email vs time)
- edge cost(more granularity)
- event topic terms and subject display
- calculating the meta graph(include pickling): takes ~ 5 mins, takes space 29M


Day 2:
- participants(needs id2email mapping)
- dynamic programming general form(Algorithm 2 missing)

Day 3:

- two baselines(greedy, random)
- documents for baseline

Day 4:

- functional tests for generating candidate trees
- experiment(greedy is better than lst?)
- measures(participants distribution entropy, topic coherence)
- greedy


Day 5:

- Discussion


# Week 3

Day 1:

- Debugging
- Found dynamic programming is not optimal
- Found a counter example

Day 2:

- Reported the Day 1 result
- Discussed/polished slides
- Came up with two algorithms:
  - Dijkstra + DP
  - PCST approximation

Day 3:

- Presentation
- Some feedback:
  - Better sampling schemes
  - Other ways to get the tree of DAG, such as minimum spanning tree
  - Joint dynamic programming(some papers by GianMarco)


Day 4:

Some ideas:

About performance(speed and optimization)

- **K-MST**: minimize edge cost subject to node coverage constraint(K-MST problem)
  - Even we can add weight to node, the *Quota problem*(almost same as K-MST) in [this paper](http://dl.acm.org/citation.cfm?id=338637)
  - The budget problem can be approximated using the quota problem routine(using binary search): set Q, solve. If edge cost is bigger than B, the half Q if smaller than B, double Q. On and on...
  - Are GW Minimization and Net Worth Maximization equavalent in approximation?
    - GW Minimization version:
	  - http://www.sciencedirect.com/science/article/pii/S0166218X03003809
	  - http://epubs.siam.org/doi/pdf/10.1137/090771429
	  - http://link.springer.com/chapter/10.1007/978-3-540-24854-5_125
	- Net worth
	  - [One paer on net worth maximization formulation](http://link.springer.com/article/10.1007/s10107-005-0660-x#page-1)


The bigger picture, is the meta-graph framework reasonable

- **Graph partitioning**: what we have done is roughtly graph partitioning(however we throw out some nodes), can we apply off-the-shell graph parititioning algogirthm?
  - Need an algorithm working with directed graph with edge cost
  - In this case, the event/partition can be a DAG
- Map the event tree back to original graph
  - What is the subgraph like?
  - How are the participants connected? Are there any patterns(star?)
- Event as DAG
  - What is the difference between event as a tree and a DAG?
  - Baseline modification: randomly/greedily grow *DAG* instead of tree
- Any baseline to operate directly on the original graph?
  - One baseline: given an event vector, select *M* nodes whose vectors are closest to the event vector.


Evaluation and summary presentation techniques

- Better evaluation?
  - Possible to pick up the nodes that are non-relevant to the event?
  - Some more sophisticated metric that topic divergence?
    - [Topic coherence metric](http://dirichlet.net/pdf/mimno11optimizing.pdf)
  - Measuring topic diversity across events?
    - Is the average distance between each of them large?
- More interpretable summarization
  - Phrases
  - Multidocument summarization
  - Information extraction?


Dataset

- Twitter dataset, what it should be like:
  - we know what events are there
  - the events should be inter-connected somehow

Day 5:

- Discussion with Kiran:
  - reply network in Twitter
  - Twitter is big
- Ask Polina:
  - one algorithm provided by her as baseline
  - what an event should be like
  
# Week 4

Day 1:

- Weekly summary
- Resource finding

Day 2:

- Tried to find algorithms for the rooted and directed k-mst
  - [this paper](http://www.csd.uwo.ca/~bma/CS873/papers/A%203-approximation%20for%20the%20minimum%20tree%20spanning%20k%20vertices.pdf) for the *undirected* version
  - Current solution: use Edmond's to get the optimal spanning tree and then greedily select the node with least edge cost
  - [Edmond's algorithm example](https://www.cs.princeton.edu/courses/archive/spring13/cos423/lectures/04DemoEdmondsBranching.pdf)
  - [Python implementation of Edmond's algo](https://github.com/mlbright/edmonds/blob/master/edmonds/edmonds.py)
  - [C++ impl](http://edmonds-alg.sourceforge.net/)
  - Which should I use? Or write my own
- Event graph structure code

Day 3:

- How about the DP algorithm for global topic divergence
- Let's check a chain/path in the tree to see if topic drift happens
- Depth/width of tree


- John Shelk, Enron vice president for governmental affairs
- Dave Perrino, Director, Government Affairs
- Jeff Dasovich, Director for State Government Affair
- Steve Kean, Lay's chief of staff
- Alan Comnes, Director Government and Regulatory Affairs
- James Steffes, former Vice President of Governmental Affairs
- Karen Denne, vice president of communications
- Ray Alvarez, Vice President- Regulatory


Day 4:

- Find some issues with the current model
  - `python event_graph_document.py tmp/result-greedy--U=0.5--dijkstra=False--timespan=28days----dist_func=cosine.pkl`
  - same messages are duplicated, for example:
    - id2count table for children: `{253809: 46, 253797: 46, 253127: 46}`
	- for all nodes: `{253797: 46, 253094: 46, 253127: 46, 253808: 46, 253809: 46, 253798: 46, 175441: 2, 253795: 1, 175479: 1, 175451: 1, 175573: 1}`
  - how to deal with this
    - construct the network in another way
- Where to get more datasets:
  - [Debian mailing list](https://lists.debian.org/)
  - Github repo issues
  - Artificial

Day 5:

- Rerun the undecomposed meta graph with reduced *U*, 0.05 and increased time span, 56 days
 - some observations: the davis event is not detected easily
 - 

# Week 5

Day 1:

- better viz for event tree
- inspected the event tree and found no obvious causal relationship
- checked out Github API + issues/pull-request
- LDA topics to 25 and experimented
- some thoughts:
  - similarity != causality: do we need a causality measure?
  - are we aiming too high(takcling both summarization and causality/information-diffusion)
  - if reply and forward exists, why not use them?
- some difference between enron and forum network:
  - enron: with real interaction, hierarchical structure, clear roles
  - forums: almost virtual, flatter structure, less clear roles

Day 2:

- decomposed case
<!-- - d3: back to original network -->
<!-- - add weights to nodes. Some nodes are more important -->


# Week 6

Day 1:

- LDA into lst repo
- Processed IslamicAwakening data
  - LDA started
  - to json for `gen_cand_trees`
  - ready to get meta graphs

Day 2:

- `gen_candidate_trees` cmd tool improvement
- trying to get `meta graph` of islamic data(12k nodes, 1000k egdes)
  - space optimization by prepruning in `get_meta_graph`
  - datetime and timestamp normalization before all things starts
- some stats when constructing meta graph:
  - 20 mins to build meta-graph
  - 5 mins to pickle the result
  - ~700M for the meta graph pickkle


Day 3:

- `filter_dag_given_root` optimized
- parallelize gen tree, failed
- run experiment for islam

Day 4:

- viz for original graph + contexted event
- experiment result for islam, except lst(slow)

Day 5:

- generalize viz and viz-preparation code, different datasets in different dir
- Run `./scripts/check_islamic_events.sh tmp/islamic/result-lst--U=5.0--dijkstra=True--timespan=28days----decompose_interactions=False--dist_func=euclidean--preprune_secs=28days.pkl` to find some patterns


# Week 7

Day 1-3:

- Finished task for Day 5 of last week

Findings on timeline viz:

- [timegliderJS](http://www.timeglider.com/widget/index.php?p=api)
- [timelineJS](https://timeline.knightlab.com/docs/index.html)


Day 4:

- variance-based optimization(speed)
- related code(for example in `gen_cand_trees`) to use variance lst
- minimum spanning tree instead of dijkstra(cmd option): **aborted**, no rooted_mst in networkx available
- sampling schemes: avoid leaf in meta-graph, give nodes with many out links high selection probability(cmd option)

Day 5:

- Bloomberg data(crawl, preprocessing)
- github repo data crawl

Day 6:

- github preprocessing
- synthetic data creation

Day 7:

- synthetic data cmd support
- event evaluation method


# Week 8:

Day 1:

- evaluation tool and some prelimenary result
- check events cmd tool
- timeline example using [vis timeline](http://visjs.org/timeline_examples.html)
  - observation on islamic data: event with only one participant(how about remove the broadcast edge?)

Day 2:

- timeline vis
  - added link type frequency
  - added event timespan
  - micro and macro view
- hint on U tool using pecentile
- enron/islamic/sklearn/bloomberg lda run
- islamic/sklearn/bloomberg metagraph generation
- synthetic experiment run on
  - U
  - sampling

Day 3:

- synthetic experiment run on
  - noise interaction number
  - preprune timespan
  - evaluation and figures(except noise interaction number)

Day 4:

- evaluation on noise interaction number(fixed sampling fraction)
- run experiment
  - bloomberg, enron multiple parameter combinations
  - islam and sklearn only one parameter set
- check dblp data(no document found)
- timeline vis for all datasets in one html page
- add "RE: " style title for github data.
- system generated text(build, etc) for github
  - user *coverall* should be removed
- rerun sklearn data
- organized viz and data prep for viz

Day 5:

- finished experiment vis
- `landscape-bot` to be removed for github

Some time stat:

- 4 mins to run *enron* experiment(without lst and variance)
- 80 mins for *sklearn* greedy, U=5.0, timespan=14days, cand\_tree\_percent=0.1, root\_sampling=out\_degree
- 71 mins for *islamic*  greedy, U=5.0,timespan=14days, cand\_tree\_percent=0.1, root\_sampling=out\_degree


Day 6:

- new way to construct metagraph for thread
- construct heterogeneous interaction graph(HIG)
- PageRank on HIG to get interaction weight
- updated greedy algorithm
- sew all the things together

Day 7:

- tune the performance of variance-based method
- experiment: 
  - islamic, sklearn with new interaction construction method and pagerank
  - synthetic data more noise

# Week 9

Day 1:

- variance cost function speed up
  - variance on enron
- ensure artificial event has meta-graph that contain all the event interactions  
- synthetic U run(including variance based)

Day 2:

- synthetic U run result(with more noise and complete trees)
  - variance-dij better than variance along
  - greedy is still the best
  - precision down and recall up is more expected than the previous experiment(with few noise)
- crawling tweets: tried to finalize it
- cleared misconception on pagerank and run enron data
- printed the result for new synthetic experiment data

Day 3:

- crawling tweet: in production now
- enron preprocessing
  - remove original message
  - lda change topic number
- BOW representation
  - combining with topic model better?
  - does not apply to variance-based method

Day 4:

- sklearn and islamic data: new interaction graph considering mentions


Plan:

- PCST algorithm
- experiment on twitter data
- check if similarity measure or document representation is good
- adding search functionality?
  - "I want to know events that about query XXX"
  
Enron:

- remove "=20"
- empty body nodes


TODO:

- noise fraction experiment
  - todo: fixed sampling **count**
- computation time comparison
- how to choose U using percentile?
- scale the node size by message count(original graph)


## Week 12

Day 2:

- PCST papers:
  - [A General Approximation Technique For Constrained Forest Problems*](http://math.mit.edu/~goemans/PAPERS/GoemansWilliamson-1995-AGeneralApproximationTechniqueForConstrainedForestProblems.pdf) and [matlab code](http://www.mathworks.com/matlabcentral/fileexchange/39916-an-approximation-solution-for-the-prize-collecting-steiner-tree-problem): undirected case
  - [Solving the Prize-Collecting Steiner Tree Problem to Optimality](http://www.siam.org/meetings/alenex05/papers/06iljubic.pdf): directed case

- A better approximation algorithm for the budget prize collecting tree problem(4-approximation)
- [Improved Approximation Algorithms for (Budgeted) Node-weighted Steiner Problems](http://arxiv.org/pdf/1304.7530.pdf): more general problem, using primal-dual method with approximation guarantee 
- [Solving the bi-objective prize-collecting Steiner tree problem with the ǫ-constraint method](http://homepage.univie.ac.at/markus.leitner/research/pub/pdf/leitner-13b.pdf): no approximation guarantee
- [Approximation Algorithms for Constrained Node Weighted Steiner Tree Problems](http://www.cs.technion.ac.il/~rabani/Papers/MossR-SICOMP-revised.pdf): log|V| approximation


## Week 13

Day 1:

- K-MST:
  - [A 2 + ε approximation algorithm for the k-MST problem](http://dl.acm.org/citation.cfm?id=338636)
  - [Saving an epsilon: a 2-approximation for the k-MST problem in graphs](http://dl.acm.org/citation.cfm?id=1060650)



Learned:

- K-MST for rooted and unrooted versions are equivalent.
- Quota can be *directly* approximated by K-MST
- Quota algorithm can be used to approximate the budget version using binary search(with 5-approximation guarantee).
- Directed version seems to be much harder than undirected version([directed steiner forest](http://crab.rutgers.edu/~guyk/pub/sf/nabs.pdf))


If modifiing of Problem 3 when modelled using quota problem.

Still maximum set cover, but the set becomes topics or hashtags. In this case, only one event in multiple events of the same topic will be covered. 



Day 2:

- Constrained forest problems with proper function:
  - T-join(shortest path and minimum-weight perfect matching as special case)
  - generalized Steiner tree(minimum spanning tree as special case)
  - point-to-point connection(fix and non-fix versions)
  - exact partitioning(tree/path/tour): using the general algorithms as subroutine and with different approximation
- Understanding the algorithm and approximation gaurantee proof

Day 3:

- Constrained forest problems with *improper* function:
  - lower capacitated partitioning problem: each component has at least k vertices
  - prize collecting (steiner tree/traveler)
- algorithm and approximation proof for PCST
- Relationship between PCST and K-MST
  - through Lagranian relaxation, K-MST becomes PCST and bounded by PCST
  - feasible solution for K-MST can be extracted by adjusting \\( \lambda \\)
  - bound proof not checked

Day 4:

- Used to think PCST for DAG is solvable for optimal solution using the greedy algorithm, however found the linear program should change for directed graph
- Formed a wrong linear program

Day 5:


- Undirected graph: S to connected-component(in other words, tree). Does the LP still gaurantee feasible solution?
  - suppose an infeasible solution exists meanwhile satisfies the constraints
    1. disconnected tree?(impossible, violates the constraints)
	2. a circle(will skip the constraints)
  - so, LP does not gaurantee a feasible solution
- Let S be tree and the degree sum function be root in-degree, does the LP hold for general diracted graph(GDG) and DAG?
  - suppose again(infeasible sol without failing consts)
  - GDG: a circle(will skip the constraint as it's not a tree). So, the LP does not hold.
  - DAG:
    - circle: no circle can exist as it's DAG
	- diamond: we can make it feasible by removing one of the edges meanwhile decreasing the obj function
  - does it make other constraints fail(conflicting constraints, only one can be satisfied)?
    - YES
  - So the modified LP does not hold
  - let's go back to the original def


Day 6:


- S unchanged(it contains covered nodes and possibly uncovered ones) and degree sum function to in-degree sum
  - will satisfication of some constraint violate those of others?
    - cannot find counter examples
  - DAG: try counter-cases
    - S = (B, A) and B -> A and C -> A: violates
    - disconnected tree? violates
	- diamond? same argument as above
  - general DiGraph:
    - circle? similar to diamond(remove one edge)



Algorithm

1. Find edge e = (i, j) with \\( i \in  C_p \in \mathcal{C}, j=C_q.root , C_q \in \mathcal{C}, C_p \neq C_q \\) that minimizes \\( \epsilon = \frac{c_e - d(j)}{f(C_q)}\\)
2. \\( F = F \cup \{e\} \\)
3. For each \\( C \in \mathcal{C} \\), \\(d(C.root) += \epsilon f(c)\)
4. the rest are the same with

Justification on the modification:

1. \\( d(i) = \sum\limits{\{C | \text{is a tree(created sometime up till now) } && C.root = i\}} y_C \\): induction(k and k+1 iteration, i is root/no-root before/after)
2. \\( \sum\limits{e \in \sigma(S)} y_S = d(j)\\), where \\( e=(i, j)\\): suppose if there is a tree \\(C\\) such that \\(y_C>0\\) and \\(j\\) is not root in \\(C\\), then the algorithm has formed such a tree before, which is a contradiction because \\(j\\) is a root in the current component.

Approximation gaurantee proof:

- left-hand side = \\( \sum\limits_{S}y_S |F^{'} \cap \sigma(S)| + \sum\limits_{j}\sum\limits_{S \subseteq C_j} y_S\\)
- At each iteraction, left-hand side increases by \\( \epsilon (\sum\limits_{v \in N_a} din_v + |N_d|) = \epsilon (\sum\limits_{v \in N_a - N_d} din_v + |N_d|) = \epsilon (|N_a-N_d| + |N_d|) = \epsilon |N_a|\\)
- At each iteraction, right hand side increases \\(\epsilon |N_a|\\)
- So it's optimal


Problem found:

1. for general DiGraph: an example where the greedy solution yields value(the lower bound) **greater** than optimal primal solution. If LP is right, then the way I calculate the LB is wrong(the algorithm can be wrong).



Irrelevant:

 - remove nodes not reachable from root for example, remove the edge C->B in case of C->B and A->B


Day 7

1. PCST + binary search
2. problem with synthetic data: multiple roots for one event



## Week 14

Day 1

- pcst for dag(attempt to prove approximation bound)
- prepare for the upper bound and re-using the result during sampling
- future plan/schedule, make it formal into list with time

- slides draft for meta-path(paper selection)
- slides draft for my own work(what to include)
- algorithm experiment on single tree

- collective classification: [short paper](http://web.cs.wpi.edu/~xkong/publications/papers/cikm12.pdf), [long paper](https://www.cs.uic.edu/~xkong/kais_mcc.pdf) and [slides](http://users.wpi.edu/~xkong/paper/cikm12_slides.pdf)

Day 2

- presentation
- problem found for PCST-DiGraph:
  - an example where suboptimal solution is found
  - Lower bound(sum of y\_s) larger than the optimal solution for integer program

Day 3

Reading about the book

Day 4:

Problem: dual objective value larger than optimal primal value

Possible causes:

- calculation(on primal and dual obj value) is wrong
- dual form is wrong
- the algorithm does not run exactly as the primal-dual form specifies
  - in the algorithm, we only choose the root to connect
  - in the mathematical form, there is no such restriction
- the minimal violation set at each iteration should not be the connected component, but is the root of the component

Now I know why the dual objective value is larger:

The basic idea of primal-dual approximation algorithm is:

- If the primal solution is infeasible, we increase the dual variables and tighten some dual constraint(s) a time and according to primal complementary slackness, we add one edge to the answer set(x_e = 1) to make the current solution less infeasible
- We iterate until the primal solution is feasible. Along the way, the dual solution remains feasible.
- We compare the dual solution against primal solution to get the approximation guarantee.


In the greedy algorithm for the undirected graph, for each iteration, we tighten one of the constraints by increasing dual variables as small as possible.

And according to the primal LP formulation for directed graph, it's ok to add edges and let one node being pointed to by more than one edge. This is undesirable, however as we want the result to by a tree and this motivates the idea of my greedy algorithm.

In the greedy algorithm, we contrain that **only** edges whose end point correspond to one of the components' root can be added. This actually eliminate the possibility of other types of edges(undesired edges discussed above) to be added.

Therefore, by adding only our target type of edges, while we tighten one of the dual constraints(the epsilon might not be the minimum we can take), some other dual constraints corresponding to the undesired edges might be **broken**. Thus, the dual solution does not necessarily remain feasible any more.

Given that dual solution can be infeasible, it's no longer a lower bound so we cannot compare its value to the primal solution.


Day 5:

- Read the book, understand how the proof for PCST is done.
- Derive an algorithm for general directed graph, which might be incorrect
- Derive the bound for general directed graph, general DAG and DAG with just one root

If we use the algorithm in Figure 4.3 in the book for directed PCST problem, the minimal violation set would be all the roots of active components. In this case, dual solution might be infeasible as dual constraints can be broken.

However, if we use all the active components as the violation set, the solution before reverse deletion can be infeasible. The reverse deletion step would not work as the input solution to it is infeasible already, how can we make it feasible after this step?

- No idea on how to formulate integer program for PCST-DAG specifically
- No idea on the algorithm if we use the original integer program
  - what is the VIOLATION-SET oracle?
- Is PCST-DAG NP-hard?
  - how is PCST NP-hard derived? derive steiner tree(ST) to PCST as ST is special case of PCST
  
Day 6&7:

Undirected

- [Algorithmic expedients for the Prize Collecting Steiner Tree Problem](http://www.sciencedirect.com/science/article/pii/S1572528610000022)
- [An Algorithmic Framework for the Exact Solution of the Prize-Collecting Steiner Tree Problem](http://homepages.cwi.nl/~klau/pubs/lwpkmf-psctp.pdf): used some directed method, worth checking, related [An Algorithmic Framework for the Exact Solution of the Prize-Collecting Steiner Tree Problem](http://search.proquest.com/docview/232850336?pq-origsite=gscholar)
  - why transform to directed version?
  - a different IP forumulation
  - some preprocessing:
    1. least-cost test: path from i to j has less cost than edge from i to j, remove the edge
  - branch-and-cut
    - insert the cut constraints(exponential) at the begining of the branching/separation step
	- why use the maxflow to find the violating constraints
  - no approximation guarantee

  
- [The Prize-collecting Steiner Tree Problem and Underground Mine Planning](https://uwaterloo.ca/computational-mathematics/sites/ca.computational-mathematics/files/uploads/files/weibei_li.pdf):K-cardinality PCST: collect only K vertices. Borrows idea from the branch-cut algorithm in the above paper
- [Algorithms for the Maximum Weight Connected Subgraph and Prize-collecting Steiner Tree Problems, 2011](http://dimacs11.cs.princeton.edu/workshop/AlthausBlumenstock.pdf): exact algorithms. reduces the size and uses mixed-integer programming. some insights on solving large steiner tree problems
- [A fast heuristic for the prize-collecting Steiner tree problem](http://www.orlabanalytics.ca/lnms/archive/v6/lnmsv6p207.pdf)
- [Combining a Memetic Algorithm with Integer Programming to Solve the Prize-Collecting Steiner Tree Problem](http://link.springer.com/chapter/10.1007%2F978-3-540-24854-5_125#page-1): finds something in the directed graph
- [On the performance of a cavity method based algorithm for the Prize-Collecting Steiner Tree Problem on graphs](http://arxiv.org/pdf/1309.0346.pdf)
- [Simultaneous Reconstruction of Multiple Signaling Pathways via the Prize-Collecting Steiner Forest Problem](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3576906/)directed or undirected networks, message passing approach
- [A Primal-Dual Clustering Technique with Applications in Network Design](http://mhbateni.com/academic/phd-thesis.pdf): PhD thesis advised by Charikar
- [An Improved LP-based Approximation for Steiner Tree](http://dl.acm.org/citation.cfm?id=1806769)

Directed:

- [Facets of two Steiner arborescence polyhedra](http://link.springer.com/article/10.1007%2FBF01586946#page-1): study the facial structure of two polyhedra associated with steiner problem
- [Approximation Algorithms for Directed Steiner Problems](https://www.cis.upenn.edu/~sudipto/mypapers/dir_steiner.pdf): with approximation guarantee
  - density(combines cost and number of terminals) as the heuristic
  - recursive definition of optimal *l*-level tree based on the result of *l-1*-level trees(inspired from the worst case example)
  - DAG has some interesting structure(for example maximum level is bounded by the depth of the tree)
- [A dual ascent approach for steiner tree problems on a directed graph](http://link.springer.com/article/10.1007%2FBF02612335)
- [A recursive greedy algorithm for walks in directed graphs](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=1530718): budgeted/capacipated prize-collecting traveling salesman(related to vehicle routing), with a reference to [A Survey on the Vehicle Routing Problem and Its Variants](http://www.scirp.org/journal/PaperInformation.aspx?PaperID=19355). What's the connection to tree?
  - recursive definition of best s-t path: best(path(s, v, B'), path(v, t, B-B')), for all mid point, v and budget allocation, B'
- [Improved approximating algorithms for Directed Steiner Forest](http://dl.acm.org/citation.cfm?id=1496870)


Budget problem


- [Fast heuristics for the Steiner tree problem with revenues, budget and hop constraints](https://www.researchgate.net/publication/222521363_Fast_heuristics_for_the_Steiner_tree_problem_with_revenues_budget_and_hop_constraints): heuristic, undirected
- [A better approximation algorithm for the budget prize collecting tree problem](http://www.sciencedirect.com/science/article/pii/S0167637703001469): undirected, (4+\epsilon)-approximation
  - applies algorithm for quota problem iteratively
- [Improved Approximation Algorithms for (Budgeted) Node-weighted Steiner Problems](http://arxiv.org/pdf/1304.7530.pdf): more general problem, using primal-dual method with approximation guarantee. node weight and cost
- [Approximation Algorithms for Constrained Node Weighted Steiner Tree Problems](http://www.cs.technion.ac.il/~rabani/Papers/MossR-SICOMP-revised.pdf): log|V| approximation



K-MST

- [Obtaining optimal k-cardinality trees fast](http://dl.acm.org/citation.cfm?id=1537600): works for undirected graph but in the algorihtm, transformed into k-Cardinality Arborescence Problem
  - why convert it to directed tree?
  - many unknown terms: maximum flow
  - practically optimal: impressive
- [Blocking optimal k-arborescences](http://arxiv.org/pdf/1507.04207v1.pdf)


Others:

- [A Compendium on Steiner Tree Problems](http://theory.cs.uni-bonn.de/info5/steinerkompendium/netcompendium.pdf): pointer to many variation of steiner tree problems
- [The Design of Approximation Algorithms](http://www.designofapproxalgs.com/book.pdf)
- [branch and cut](http://homepages.rpi.edu/~mitchj/papers/bc_hao.pdf)
- [branch and bound](http://www.imada.sdu.dk/Employees/jbj/heuristikker/TSPtext.pdf)



## Week 15

Day 1

- PCST optimal paper(can we apply branch and cut to the DAG problem?)
  - I guess we can, but how?
- paper suggested by Aris
  - answer relationship queries over large graph, modeled as steiner tree problem
  - with approximation guarantee
  - also algorithm top-k steiner trees to given query
  - two phases
    - tree generation
	- loose path replacement
  - top-k steinter trees
    - based on the tree from the first algorithm, turbulate the loose paths by adding weights so that new replacement can be found
	- improve the tree based on the new replacements
- Polina's suggested paper on Steiner tree on directed graph
- Organize my words and discussion


What to discuss:

**PCST**:

- why I work on PCST
  - the road map: PCST->MST->Quota->Budget
  - [PCST->MST](http://theory.stanford.edu/~tim/papers/kmst.pdf)
  - MST = Quota
  - [Quota -> Budget](http://dl.acm.org/citation.cfm?id=338637): how the 5-approximation comes?
  - that's for **undirected** case  
- incorrectness of the proof on the greedy primal-dual method
  - [the chapter](http://math.mit.edu/~goemans/PAPERS/book-ch4.pdf)
  - Def of minimal violation set in Figure 4.3 will be the roots of active components. Then dual constraints might be broken.
  - However, if we let the violation set be all the active components and their subset, solution feasibility is not guaranteed. Even the reverse deletion step will not help.
  - No idea on how to formulate integer program for PCST-DAG specifically
  - No idea on the algorithm if we use the original integer program: specifically, what is the VIOLATION-SET oracle?
    - generate feasible solution
	- does not violate any dual constraints so that approximation guarantee can be proved
- Is PCST-DAG NP-hard?
  - how is PCST NP-hard derived? derive steiner tree(ST) to PCST as ST is special case of PCST
- PCST-dag is NP-hard because Steiner-DAG is NP-hard and Steiner-DAG is special case of PCST-DAG
  - (root, set node) with weight 1
  - (set node, element node) with weight 0
- for directed case: I only found resources for steiner problem
  - check out [A Compendium on Steiner Tree Problems](http://theory.cs.uni-bonn.de/info5/steinerkompendium/netcompendium.pdf)
    - 1.32 budget problem
  - [Approximation Algorithms for Directed Steiner Problems](https://www.cis.upenn.edu/~sudipto/mypapers/dir_steiner.pdf): with approximation guarantee
    - density(combines cost and number of terminals) as the heuristic, high density is more likely to lead to near-optimal solution
    - recursive definition of optimal *l*-level tree based on the result of *l-1*-level trees(inspired from the worst case example)
  - [a series of ...](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.112.8906&rep=rep1&type=pdf)
- branch-and-cut algorithm by Ivana seems to be more general:
  - [the paper](http://homepages.cwi.nl/~klau/pubs/lwpkmf-psctp.pdf): how to prove the approximation ratio
    - why transform to directed version?
    - a different IP forumulation
    - some preprocessing:
      1. least-cost test: path from i to j has less cost than edge from i to j, remove the edge
    - branch-and-cut
      - insert the cut constraints(exponential) at the begining of the branching/separation step
      - why use the maxflow to find the violating constraints
    - no approximation guarantee

**Sampling**:

- checked the query paper:
  - it focues on modifying the result on the same tree
  - however, we want to find trees on different parts of the graph
- the root sampling stragegy
  - simple upperbound and pruning using threshold
    - determining the threshold: U / average edge cost
  - further sample by heuristic by choosing either of the following:
    - exploitation: subtree that has high log|V| * |V| / |C|(or simply density thresholded by subtree size) is more promising, we maintain a fixed-size queue for those roots
	- exploration: select those with high upper bound
	- probability to explore depends on how much we have covered the all nodes. For example, we covered 90% of the nodes, then the proba to explore is 0.1
  - a pipline to add sampling preference to roots(**maybe overkilling**):
    - sample roots that are at the peak of the frequency against time
    - dense subgraph detection to identify candidates
	- preference on people/interaction on the dense interaction subgraph

About future plan:

- working out PCST for DAG is not very promising(no existing work on that), we might try some heuristics or work it out later



- can we modify the problem definition somehow to circumvent this issue(unable to find algorithms for budget-DAG)?
- my worry about the semantic drift
- for directed case: I only found resources for steiner problem
  - how about the paper suggested by Polina?


Discussion result:

- focus on the Charikar paper and primal-dual methods
- maintain a lower bound of the top-k best non-overlapping(the invariant) trees
  - if the upper bound of a candidate is lower than the lower bound, throw it away
  - if greater, issue arises when the tree overlaps with **multiple** trees in top-k list
     - need some way to update the list
	 - compare sum of trees? might reject some earlier rejected but promising trees(introduces dependency among the trees)
	 - how about top-(n x k) list?
	 - or loosen the invariant, e,g, allows some level of overlapping

Next week:

- read the Charikar paper
- read the 2-approximation k-mst paper
- primal-dual method for directed graph?
  - different formulation(Ivana's paper)?
  - what's the violation set oracle?
- check papers on generating simulated interaction data and experiment
- Give a shot to search root sampling stuff
  - can we reuse the intermediate result
  - oh, check Gianmarco's paper

Done:

- paper suggested by Aris

Day 2:

The paper:

- doesn't necessarily hold: all terminals are at the leaves of any steiner tree(for k-mst problem, this does not hold)(P4)
  - cannot see why it's needed for the proof
- why use the transitive closure?(P6)

cannot see how the proof/algorithm handles circles explicitly, actually the algorithm can handle circle. For example:


    G = (r->v->u->r), a circle and all nodes are terminals

    A_3(4, r, {v, u}) = {(r, v)} + A_2(3, v, {u})

    A_2(3, v, {u}) would not connect u->r because it calls A_1(2, u, {}), which connects nothing



- does being DAG change the approximation guarantee?
- can we take advantage that V=T in k-msa to improve the algorithm/approximation ratio?


Learned:

For both problems(D-STEINER and DG-STEINER):

- notion of bunch:
  - D-STEINER: a subtree with intermediate node connecting to terminals through shortest path, so that some edge costs can be shared across multiple root-terminal paths
  - DG-STEINER: 
- use *density* of bunch as the quality of the subtree
  - technically not special
  - the special thing is the approximation guarantee

For DAG, consider the questions:

1. **Q**: Is the algorithm slowed by the fact that the graph is cyclic?
  - circle like `a->b->c->a`, run `A_9(10, a, {b, c})`, will be trapped temporarily in the recursion.
  - Get around this: pass in the ancestors and prevent the `r` in `A_l(k, r, X)` collide with any ancestors.
  - for DAG, not necessary to do so
  - a second thought, what should `A_6(8, c, {})` return?
    - return nothing, because we don't need to cover anything, why bother adding edges?
	- so, no need for the above, when `X=\emptyset`, return nothing
2. **Q**: Is the result worsened by the fact that the graph is cyclic? Can we have such example?
  - currently no. Example: A->B:3, A->C:1, B->C:0, C->B:1, but algorithm is not tricked
  - or question: is there a circle that makes the algorithm to choose a subtoptimal solution instead of optimal one?
  - what does it mean by a circle? getting back to the starting node. Will the algorithm get a better solution by getting back to the starting node? No, if it has been to that node, why being there again?
3. **Q**: can we make the algorithm faster by the fact that all nodes are terminals(the k-msa problem)


pruning `X`

  - for DAG, we can prune the `X` more efficienly by choosing only the descendants of `r`
  - this will improve practical time complexity, however not asymptomatically
For k-msa-DAG, any speed up? If we use the original algorithm, the time complexity upperbound does not change.

Any modification to the following notions:

- Bunch:
- density: 

Day 3:

- the remaining questions
  - do we need to impose transitive constraints on it?
  - if so, we need to track the nodes being covered by each shortcut edge, for example given a->b->c, and shortcut a->c, if we connect a->c, then b should be covered(removed from X if it's terminal)
  - I guess we need to, because if not and if the tree is deep, then we need to make `l` large in order to get good results. However, we might not be able to afford the time complexity.
- papers citing D-STEINER paper
  - [On directed Steiner trees](http://dl.acm.org/citation.cfm?id=545388): Primal dual formulation
  - [FasterDSP: A Faster Approximation Algorithm for Directed Steiner Tree Problem](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.118.9349): faster and points out some **problems** with the approximation proof in Charikar paper
  - [Approximation Algorithms for the Maximum Leaf Spanning Tree Problem on Acyclic Digraphs](http://link.springer.com/chapter/10.1007/978-3-642-29116-6_7#page-1): mentioned the DAG and general DiGraph yields the same approximation ratio(P3)
- from mst to budget, what's the approximation ratio
  - the [PCST theory and practice paper](http://dl.acm.org/citation.cfm?id=338637) showed that 3-approximation quota problem(rooted/unrooted) lead to (5+\epsilon) for unrooted case
  - [improved 4-approximation algorithm](http://ac.els-cdn.com/S0167637703001469/1-s2.0-S0167637703001469-main.pdf?_tid=231d1450-e075-11e5-b872-00000aacb361&acdnat=1456923121_1bfc86c02df3aa806af485d7d9122c67)
    - mentioned Hassin's geometric-mean binary search that further reduces time complexity
    - why decompose and why to 4 sub-trees?
	  - by decomposing, we can find subtrees that are bounded by `B`
	  - for 4, I guess in such a way, each subtree can have a minimum sum of prize
	- difference between this split tree approach and changing `Q` until exceeding `B` approach?
	  - by former one, we can have approximation bound
	  - the binary search one maintains lower and upper bound on `Q` and search between until the bounds are close enough
    - can we apply the similar approach(with approximation bound) to D-STEINER?
	  - the approximation ratio for D-STEINER is `\alpha=i(i-1)k^{1/i}`, can we divide the tree with cost `\le \alpha B` into subtrees each of whose cost is smaller than `B` and reward greater than something?
	  - yes, we can. by applying the `tree_cover` procedure, we can generate a set of trees with `B/2 <= c(T) <= B`, thus the set size is at most `ceil(2 \alpha)`. Thus, the approximation ratio for D-BUDGET is `ceil(2 \alpha)`.
- large scale k-mst/steiner
  - [Fast Approximation of Steiner Trees in Large Graphs](http://ldbcouncil.org/sites/default/files/Fast%20Approximation%20of%20Steiner%20Trees%20in%20Large%20Graphs.pdf)
  - [Local Search for Hop-constrained Directed Steiner Tree Problem](http://liu.diva-portal.org/smash/get/diva2:739485/FULLTEXT03.pdf)
- paper on simulating interactions
  - [Dynamics of Conversations](http://mahdian.org/threads.pdf): model for generation of basic conversation structure
  - [Information Propagation on Twitter](http://snap.stanford.edu/class/cs224w-2010/proj2009/TwitterWriteup_Sadikov.pdf): analysis on twitter social network properties, measure external influence
- read approximation algorithms


Day 4:

read the FasterDSP paper:

- TM algorithm works for directed tree, but with approximation guarantee `O(k)`
- Z's lemma about l-level tree is incorrect, this paper corrects it and consequently, Charikar's approximation guarantee changes
- uncovered set: why this definition? how does it decide the approximation guarantee?
- duplicate cases in Charikar's algorithm? What does it mean?

no easy to understand. some notation are not clear, plus some typo plus not a famous journal. I decided to give it up.

Read the introduction part of the book

Day 5

Went through the proof of B/2 <= c(T') <= B and had some testcases in mind
  - all edge cost = 1
  - A->B=0.1, A->C=0.1, B->E=2

Z paper:

  - full steiner tree: tree such that all leaves are terminals and root belongs to terminal \cup {r}
  - constructs the final result by merging multiple full steiner trees
  - approximation ratio is exponential to l compared to the polynomial ratio in Charikar's algorithm

Recap of Charikar's algorithm:

1. if we can improve the approximation factor of Charikar's algorithm for DAG, it implies circles trick Charikar's algorithm to achieve worse. But what's the point of circle? Getting back to itself. First, there cannot be circle in a tree. Second, what benefit does getting back to one node bring when constructing a steiner tree
2. the algorithm handles circle: when there is a circle(`a->b->c->a`), `A_2(1, c, {})` should return nothing.

Making it faster for DAG:

1. as recursion goes deeper, number of nodes to consider shrinks. But asympototically, it's the same as general graph.
2. memoization to cache result

From k-msa to budget problem:

Suppose `OPT` is the optimal value for the budget problem with `B`. If `Q <= OPT`, `c(T) <= \alpha B `. Thus, we increase `Q` geometrically as long as it stays under the bound. So finally `OPT/(1+\epsilon) <= Q <= OPT`. For the resulting tree `T`, we can split into `N` subtrees such that they cover `T` and the average cost of subtree stays between `[B/2, B]`. Thus there can be at most `\beta = 2 * floor(\alpha) + round(mod(\alpha), 1)` subtrees and their reward is at least `OPT / (1+\epsilon) / \beta`.

Sampling stuff

**Approach 1:**

maintian a priority queue(fixed size) by ranked the size of the computed event tree.

For a new coming root, it  can be dropped when satisfying either of the following cases:

1. if its upper bound is lower than the minimum element in the queue(it has no hope to get into the queue)
2. if the input DAG has some node intersection with any tree in the queue

Case 2 might cause problem when the new root can lead to a huge tree, which however intersects with some trees in Q.

- If there is only one intersected tree, just replace the smaller one if possible.
- If have multiple intersections, things become complicated.
  - is the probability high?
  - one thing is sure: to maintain the invariant, we can either drop the new tree and all the intersected trees in Q
  - If the tree is relatively small, we can drop it
  - if tree is large, can we drop it?
    - tree size is bigger than the total, keep it
	- example: `A \cap B \cap C != \emptyset` and `B` is the new tree, they are of similar size, what to do?
- It seems that we are mixing the k maximum set cover problem with the root sampling problem
  - we can increase the queue size(introduces another parameter)

Some improvement:

- some stopping criteria, for example coverage:
- ordering of the node

Benefit:

- simple to implement


First question, how many trees to choose?

**Approach 2:**

At each iteraction, we have a probability of either explore or exploit:

1. explore: select a root that has **not** been covered by any trees computed before
  - node with higher upper bound is more likely to be selected
  - or rooted tree without any intersection (more computation)
2. exploit: select a root that has been covered by any trees computed before
  - node with higher (partially-computed) density x log(size) is more likely to be selected

The exploration/exploitation probability changes as we cover more nodes

Problem:

- when to stop
  - when coverage is beyond threshold(e.g, 90%)
  - how to set the threshold?
- can we drop some trees with low upperbound?
  - before we start, set some threshold
  - cutting by upperbound is implicitly used as during the exploration step, we only select the high upperbound roots and we stop when coverage is reached

Benefit:

- separating the problem clearly


## Week 16


Day 1

check the proof of the 4-approximation algorithm

`OPT` is the optimal value for budget problem given budget `B`.

If `Q <= OPT`, then `cost(T) <= \alpha B`, this is obvious by def of approximation factor on the quota problem algorithm
If `cost(T) <= \alpha B`, then `Q <= OPT`. Can be shown by contradiction.

Suppose, `Q > OPT`, then algorithm on quota problem can produce a tree with quota `>OPT` and budget `<=\alpha B`. Using "reverse" definition of approximation factor, there is some solution that achieves `Q' > OPT` using budget `<= B`. This is contradictory to the optimality for `OPT` given budget `B`. 


[Dynamics of Conversations](http://mahdian.org/threads.pdf): model that generates a thread conversation that considers time and author.

- can be used to generate a conversation
  - with only reply relationship
  - recipient info is not explicit
- however, need to add topic vector to each message
  - maybe we can consider topic shift, which is more realistic

One approach:

- at each step, one of the current participants can do one of the following based on an old message:
  - reply
  - forward
  - create new
- as for which message is the new message based on, the more recent the old message, the more likely it's based on
- as for newly created message, some (larger) topic shift is inserted
- in such as way, we know the true propagation event
- when constructing the meta-graph, we don't know such structure and use the tree rules to construct such graph.
- in the end, we compare the resulting tree with the true event tree
  - any tree similarity/distance measure?

We can make it even harder, generate one main event and several smaller noisy events. See if the algorithm can find the true event.

Some thinking on the meta graph construction process:

- can we explicitly use the forward/reply relationship in the network:
  - for example, in twitter, whether a tweet is a retweet(forward) can be known
  - or in email network, forward, reply can be known also from the title
    - can we get this type of information from the Enron dataset(the MySQL data)?
- why do we explicitly use this?
  - because if we use the simple rule(3 types), then redundant edges will be created
  - for example: we know that: 1, A sent to B, 2, B replied to A, 3, A replied to B
    - ideally: 1->2->3 is enough
	- if we use our rule, there will be an extra 1->3, which is unnecessary

Some justification on why using tree:


1. [Tracing information flow on a global scale using Internet chain-letter data](http://www.pnas.org/content/105/12/4633.full.pdf):
  - highlight: use tree to represent information flow
  - construct a network where nodes are people
  - the induced tree is deep and narrow
2. tree is natural:
  - for example, forum thread(nested structure)


Day 2:

- tree generation algorithm
- single tree experiment code
  - `make_artificial_data`: for each event, dump also `preprune_seconds`, `root`, `U`
  - `gen_cand_trees`: `--roots` argument
  - `synthetic_different_noise_fraction.sh`: to bundle them up
- write
  - find the template and sketch out the paper structure, e.g, section name and what to include
  - problem definition
- read the book

Day 3:

- `synthetic_evaluation`: `noise_fraction`
  - find some metric to use
    - found the [apted](http://tree-edit-distance.dbresearch.uni-salzburg.at/#ted)
	- however, it's a distance, how to make into similarity
	- problem: the edit distance can be larger than the size of any of the trees
  - finish the code `def evaluate_single_tree`
- Charikar's algorithm
  - test cases
  - algorithm
- think about synthetic data
  - how noise interactions should be added, pros and cons
    - should the event and noise grow together? instead of randomly adding some noises?
  - how to add semantic shift(the repr vector)?
- approximation proof for budget problem
- move the following to pkdd draft
  - NP-hard proof
  - algorithm(modify the notation if necessary)

