import unittest
import pm4py

from process_miner.logger import Logger
from process_miner.miners.heuristic import HeuristicMiner
from process_miner.miners.xesparser import XESParser
from tests.utils import utils


class HeuristicTests(unittest.TestCase, utils):

    def runTests(self):
        tests_to_run = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
        for t in tests_to_run:
            self.testDynamic(t)

    def testDynamic(self, file):
        # load file from file path and parse
        filepath = f"resources/{file}.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser(Logger())
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()

        # Run my heuristic miner
        hm = HeuristicMiner()
        hm.run(traces_df)
        dependency_measure_matrix = hm.get_dependency_measure_matrix()
        succession_matrix = hm.get_succession_matrix()

        # Run the pm4py heuristic miner as an oracle
        log = pm4py.read_xes(filepath)
        heu_net = pm4py.discover_heuristics_net(log, dependency_threshold=-1)
        dependency_measure_matrix_oracle = heu_net.dependency_matrix
        succession_matrix_oracle = heu_net.dfg_matrix

        # Compare results
        for a in heu_net.activities:
            for b in heu_net.activities:
                if a in succession_matrix_oracle and b in succession_matrix_oracle[a]:
                    self.assertEqual(succession_matrix_oracle[a][b], succession_matrix[a][b])
                    """
                    Only compare dependency measure matrix if there is an entry in the succession Matrix for this
                     combination. Reason being the difference between the implementation of the heuristic miner in the 
                     book vs by pm4py.
                     pm4py does not consider negative relations in it's dependency measure matrix - e.g. in L1.xes* the
                     dependency measure between b and a  would be -3/4 = (0-3) / (0+3+1) = |b>a|-|a>b| / |b>a|+|a>b|+1.
                     This dependency measure is just filtered by the UI in my solution (occurrences > 0), while pm4py
                     does not even include it in the dependency matrix.
                     
                     *L = {(a,b,c,d)^3, (a,c,b,d)^2, (a,e,d)}                    
                     """

                    if a in dependency_measure_matrix_oracle and b in dependency_measure_matrix_oracle[a]:
                        self.assertEqual(dependency_measure_matrix_oracle[a][b], dependency_measure_matrix[a][b])
                    else:
                        self.assertEqual(0.0, dependency_measure_matrix[a][b])
                else:
                    self.assertEqual(0.0, succession_matrix[a][b])


if __name__ == '__main__':
    unittest.main()
