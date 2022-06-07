import unittest

from process_miner.miners.alpha import AlphaMiner
from process_miner.miners.xesparser import XESParser
import pandas as pd
from io import StringIO


class AlphaMinerTests(unittest.TestCase):

    def test(self):
        testFiles = ['L1', 'L2', 'L3']
        for i in testFiles:
            self.runTest(i)

    def runTest(self, file):
        filepath = f"resources/{file}.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser()
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()
        miner = AlphaMiner()
        miner.run(traces_df)
        loc_csv = miner.get_location_csv()
        trans_csv = miner.get_transition_csv()
        loc_oracle_df = pd.read_csv(f"resources/{file}-loc-oracle.csv").sort_values(['loc', 'type']).reset_index(drop=True)
        trans_oracle_df = pd.read_csv(f"resources/{file}-trans-oracle.csv").sort_values(['source', 'target', 'type']).reset_index(drop=True)
        loc_actual_df = pd.read_csv(StringIO(loc_csv)).sort_values(['loc', 'type']).reset_index(drop=True)
        trans_actual_df = pd.read_csv(StringIO(trans_csv)).sort_values(['source', 'target', 'type']).reset_index(drop=True)
        self.assertEqual(len(loc_oracle_df.compare(loc_actual_df).index), 0)
        self.assertEqual(len(trans_oracle_df.compare(trans_actual_df).index), 0)

    @staticmethod
    def load_test_file(filepath):
        f = open(filepath, "r")
        test_xml_string = f.read()
        f.close()
        return test_xml_string


if __name__ == '__main__':
    unittest.main()
