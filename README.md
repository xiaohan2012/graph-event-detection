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
- event topic terms

- participants(needs id2email mapping)

Day 2:

- Algorithm 2
- parameter tuning(embedded task)

