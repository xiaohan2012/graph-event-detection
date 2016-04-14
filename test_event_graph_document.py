import os
import unittest
import cPickle as pkl
from nose.tools import assert_equal, assert_true

from .test_util import CURDIR
from .events import detect_events
from .event_graph_document import children_documents, longest_path_documents
from .util import load_id2obj_dict
from .dag_util import get_roots


# class EventGraphDocumentTest(unittest.TestCase):
#     def setUp(self):
#         candidate_events = pkl.load(open(
#             os.path.join(CURDIR, 'test/data/cand_trees.pkl')))
#         self.g = detect_events(candidate_events, 1)[0]
#         self.mid2interaction = load_id2obj_dict(
#             os.path.join(CURDIR,
#                          'test/data/enron-whole.json'),
#             'message_id'
#         )

#     def test_children_documents(self):
#         roots = get_roots(self.g)
#         assert_equal(1, len(roots))
#         documents = children_documents(self.g, roots[0],
#                                        self.mid2interaction)
#         assert_equal(len(documents), 138)
#         for d in documents:
#             assert_true('message_id' in d)
#             assert_true('subject' in d)
#             assert_true('body' in d)

#         assert_true(documents[0]['subject'].startswith('Energy Issues'))
#         assert_true(documents[0]['body'].startswith(
#             'Please see the following articles'))
                
#     def test_longest_path_documents(self):
#         roots = get_roots(self.g)
#         docs = longest_path_documents(self.g, roots[0],
#                                       self.mid2interaction)
#         assert_equal(5, len(docs))
#         assert_true(docs[0]['subject'].startswith('Energy Issues'))

