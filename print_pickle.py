import sys
import cPickle as pkl
from pprint import pprint

pprint(pkl.load(open(sys.argv[1])))
