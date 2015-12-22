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
- d3: back to original network
- add weights to nodes. Some nodes are more important


Problem with decomposition:

For `lda-25-topics/result-lst--U=10.0--dijkstra=True--timespan=56days----decompose_interactions=True--dist_func=euclidean.pkl`

'children documents count: Counter({253797: 46, 253798: 46, 253127: 46, 253808: 46, 253809: 46, 253094: 46})'
'all documents count: Counter({253797: 46, 253798: 46, 253127: 46, 253808: 46, 253809: 46, 253094: 46, 121758: 12, 122436: 8, 253795: 1, 121747: 1, 253108: 1})'
'longest path documents count: Counter({122436: 1, 253795: 1, 253108: 1, 253127: 1})'
"longest path documents' subject: [u'Energy Issues', u'Energy Issues', u'More info from ISO -- May be Providing Confidential Data to State', u'Fwd: New York Times - Plan on California Energy Has No\\tShortage of Critics']"


+----+-----------------------------------------------------------------------------------------------------+------+------+------+------+------+---------+
|    |                                                                                                     |   #1 |   #2 |   #3 |   #4 |   #5 |   total |
|----+-----------------------------------------------------------------------------------------------------+------+------+------+------+------+---------|
|  7 | lst--U=5.0--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=euclidean    |   39 |   25 |   24 |   24 |   23 |     135 |
|  6 | lst--U=5.0--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func=euclidean    |   34 |   23 |   21 |   20 |   20 |     118 |
|  0 | greedy--U=5.0--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=euclidean |   33 |   24 |   19 |   19 |   19 |     114 |
|  5 | lst--U=5.0--dijkstra=False--timespan=14days----decompose_interactions=False--dist_func=euclidean    |   33 |   21 |   19 |   17 |   15 |     105 |
|  4 | greedy--U=5.0--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func=euclidean |   25 |   19 |   18 |   17 |   17 |      96 |
|  1 | lst--U=5.0--dijkstra=True--timespan=56days----decompose_interactions=False--dist_func=euclidean     |   29 |   17 |   16 |   16 |   14 |      92 |
|  3 | greedy--U=5.0--dijkstra=False--timespan=14days----decompose_interactions=False--dist_func=euclidean |   25 |   17 |   16 |   15 |   15 |      88 |
|  9 | lst--U=5.0--dijkstra=True--timespan=28days----decompose_interactions=False--dist_func=euclidean     |   22 |   15 |   14 |   14 |   13 |      78 |
|  8 | lst--U=5.0--dijkstra=True--timespan=14days----decompose_interactions=False--dist_func=euclidean     |   19 |   14 |   13 |   12 |   12 |      69 |
|  2 | random--U=5.0--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=euclidean |   13 |   12 |   11 |   11 |   11 |      58 |
| 10 | random--U=5.0--dijkstra=False--timespan=14days----decompose_interactions=False--dist_func=euclidean |   12 |   12 |   11 |   11 |   11 |      57 |
| 11 | random--U=5.0--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func=euclidean |   14 |   12 |   11 |   10 |   10 |      57 |
+----+-----------------------------------------------------------------------------------------------------+------+------+------+------+------+---------+


Topics:

```
iso report apx markets order things capacity supply board demand
davis utilities governor plan edison political crisis lines plants billion
bush words davis president news times los angeles tuesday edition
dow jones service natural customers coal bank deal sempra percent
trading million plant percent companies williams wed june times generators
april utility tax words utilities times companies cpuc san edition
barton legislation language draft house epsa rto amendment hearing nerc
vince kaminski june risk management communications mailto talk martin mike
wagner settlement judge davis billion gao exchange refunds sources refund
edison april davis commission natural bankruptcy utility federal san thursday
davis utilities edison billion federal generators commission blackouts million pay
policies procedures extension services enronxgate trading employees access legalonline compliance
azurix india board units support air clean employees office law
http intended recipient email attachments paper distribution mailto delete contact
enronxgate ken susan robert paul linda karen comments joe david
skilling communications employees enronxgate corporate policy michael stock program mike
participant subpoena fax cpuc calpx request data tel exchange number
transmission nerc system services ets sarah september markets gss christi
credit iep assembly costs alan refund burton senate comnes dasovich
utilities davis utility plants customers edison contracts summer plant consumers
stock companies natural oil share customers index tnpc top earnings
kevin michelle ena relationship fred mailto contact term lead gerry
panama sce cash april taken projects site access actions gavin
times senate electric language lockyer sports reliability national interstate print
davis generators blackouts federal caps commission wed order plants plant
```

`lda-25-topics/result-lst--U=5.0--dijkstra=False--timespan=14days----decompose_interactions=False--dist_func=euclidean.pkl`

|          |   #nodes | time                  | subject(root)                                                                                                                | terms                                                                                  |
|----------+----------+-----------------------+------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------|
| **#1,**  |       33 | 2001-07-06 2001-07-19 | Re: UC-CSU-Enron press release                                                                                               | iso davis enronxgate utilities commission transmission markets order electric report   |
| **#2,**  |       21 | 2001-06-14 2001-06-28 | RE:                                                                                                                          | iso enronxgate draft markets data order http vince report transmission                 |
| **#3,**  |       19 | 2001-02-28 2001-03-14 | Re: followup to telephone conversation of 3-7-01                                                                             | davis utilities edison billion million generators federal utility companies plants     |
| **#4,**  |       17 | 2000-08-14 2000-08-25 | Talking Points re "reregulation" in California                                                                               | iso enronxgate markets order draft report services http data transmission              |
| **#5,**  |       15 | 2001-04-28 2001-05-11 | CAISO NOTICE: Freedom of Information Request of confidential atta chments to the DMA report filed with FERC on March 1, 2001 | iso enronxgate markets draft order data report services http susan                     |
| **#6,**  |       15 | 2001-04-04 2001-04-17 | Call to Bob Glynn                                                                                                            | bush words president news iso communications ken times services tuesday                |
| **#7,**  |       15 | 2001-06-07 2001-06-21 | White House To Support FERC Action Today                                                                                     | iso enronxgate davis bush commission markets order utilities president times           |
| **#8,**  |       15 | 2001-05-13 2001-05-25 | Re: Gov Geringer meeting                                                                                                     | iso bush words enronxgate president news communications ken services markets           |
| **#9,**  |       14 | 2000-09-20 2000-10-04 | Re: RGA request                                                                                                              | davis utilities federal times commission edison bush companies iso utility             |
| **#10,** |       14 | 2000-08-29 2000-09-10 | Carin Energy Rumor                                                                                                           | davis utilities iso times federal commission bush companies edison million             |
| **#11,** |       14 | 2000-07-24 2000-08-07 | Re: Doctoral studies                                                                                                         | iso enronxgate markets draft order services report data http susan                     |
| **#12,** |       14 | 2001-09-06 2001-09-20 | Senate Energy Markup Cancelled                                                                                               | iso enronxgate draft markets data order vince http transmission report                 |
| **#13,** |       14 | 2001-03-21 2001-04-03 | Board presentations                                                                                                          | davis utilities billion million edison companies generators blackouts federal times    |
| **#14,** |       13 | 2001-10-11 2001-10-24 | RE: Southern Co.'s Testimony                                                                                                 | iso enronxgate draft markets data order vince http transmission report                 |
| **#15,** |       14 | 2001-03-12 2001-03-23 | Revised Merger Release & Q&A                                                                                                 | bush words president news times communications ken tuesday section government          |
| **#16,** |       12 | 2001-07-27 2001-08-09 | Energy Issues                                                                                                                | davis utilities iso edison billion million commission generators federal companies     |
| **#17,** |       11 | 2000-10-04 2000-10-16 | Enron's policy on Libya                                                                                                      | iso enronxgate bush markets services words order president communications ken          |
| **#18,** |       10 | 2001-06-21 2001-07-05 | Customers                                                                                                                    | iso bush enronxgate words president news services communications ken markets           |
| **#19,** |       10 | 2001-09-25 2001-10-09 | RE: EPSA/EEI on Reliability                                                                                                  | iso enronxgate draft markets data order transmission http report vince                 |
| **#20,** |       10 | 2001-11-10 2001-11-21 | FW: Confidential - GSS Organization Value to ETS                                                                             | davis utilities times companies million billion bush edison federal generators         |
| **#21,** |       13 | 2000-09-10 2000-09-24 | Re: Two Governor's Press Releases--More Courage from the Capitol                                                             | davis utilities bush federal times commission president edison governor companies      |
| **#22,** |       10 | 2000-04-11 2000-04-20 | Something to shoot at--California                                                                                            | iso bush words president news enronxgate communications ken times services             |
| **#23,** |       21 | 2001-07-11 2001-07-19 | Re: FERC course on for Thurs, July 26, 1-4 p.m.                                                                              | iso davis enronxgate utilities commission transmission federal markets electric system |
| **#24,** |       12 | 2000-07-17 2000-07-31 | Re: Canary Wharf - Update for Executive Committee                                                                            | iso enronxgate bush words services markets president communications ken news           |
| **#25,** |       14 | 2000-08-09 2000-08-21 | California Update                                                                                                            | iso enronxgate bush markets services order words report communications ken             |
