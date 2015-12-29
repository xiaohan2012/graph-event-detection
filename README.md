# lst
length-constrained maximum-sum subtree algorithms


# Processing of messages

- "= \ " to ""
- "\ " to " "
- "=\r\n" to ""
- "\r\n=" to ""
- "[IMAGE]" to ""
- "\r\n" to " "
- "\n" to " " \# collapse to one line

Def of word:

1. only alphabetic letters: 13041 unique tokens
2. otherwise:  21862 unique tokens


# Topics

1. davis utilities san plant plants times million utility blackouts generators commission customers trading companies percent electric officials federal wed edison [California eletricity crisis](https://en.wikipedia.org/wiki/California_electricity_crisis)
2. ect iso enronxgate amto confidential report draft enroncc susan joe communications ken comments order david june transmission markets language chairman [Ken's email](https://www.cs.umd.edu/~golbeck/perl/examples/KenLayEmail.txt)
3. bush jones president dow stock bank companies trading dynegy confidential news service natural oil credit services copyright deal percent policies [Bush and Ken Lay: Slip Slidin' Away](https://consortiumnews.com/Print/020602.html)
4. davis utilities edison billion federal generators utility commission governor plan million crisis san plants electric pay companies thursday iso southern. [Davis buy transmission lines](http://www.consumerwatchdog.org/story/davis-reaches-deal-edison-buy-transmission-lines-27-billion)


# Resources

- [Enron Crisis Timeline](https://www.ferc.gov/industries/electric/indus-act/wec/chron/chronology.pdf)


# Dairy

## Week 1(Nov 23)

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

## Week 2

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


## Week 3

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
  
## Week 4

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

## Week 5

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