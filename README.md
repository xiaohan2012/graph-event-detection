# lst
length-constrained maximum-sum subtree algorithms


# Processing of enron messages

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

# Valid interaction.json

should contain fields:

- message_id
- subject
- body
- timestamp
- datetime(*optional*)
- *sender_id*
- *recipient_ids*

For the last two fields, it can be replaced by `participant_ids`


# 

`gen_cand_trees.sh` and `check_events.sh`
