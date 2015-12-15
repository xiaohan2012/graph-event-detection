import unittest
import os
from nose.tools import assert_true

from .test_util import CURDIR, remove_tmp_data
from .event_graph_structure import plot_graphs, plot_events
from .events import detect_events_given_path


class EventGraphStructureTest(unittest.TestCase):
    def setUp(self):
        self.figure_dir = os.path.join(CURDIR,
                                       'test/data/figures')
        if not os.path.exists(self.figure_dir):
            os.makedirs(self.figure_dir)
        result_path = os.path.join(CURDIR, 'test/data/candidate_trees.pkl')
        self.K = 5
        self.events = detect_events_given_path(result_path, self.K)
        
    def _check_files_exist(self):
        for i in xrange(1, self.K):
            assert_true(
                os.path.exists(
                    os.path.join(self.figure_dir, '{}.png'.format(i))
                )
            )

    def test_plot_events(self):
        plot_events(self.events, self.figure_dir)
        self._check_files_exist()

    def test_plot_graphs(self):
        plot_graphs(self.events, self.figure_dir)
        self._check_files_exist()

    def tearDown(self):
        remove_tmp_data(self.figure_dir + '/*')
