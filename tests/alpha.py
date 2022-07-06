import unittest

from process_miner.miners.alpha import AlphaMiner
from process_miner.miners.xesparser import XESParser
import pandas as pd
from io import StringIO

from tests.utils import utils


class AlphaMinerTests(unittest.TestCase, utils):

    # Main test method
    def test(self):
        testFiles = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
        for i in testFiles:
            self.runTest(i)

    # Test runner
    def runTest(self, file):
        # load file from file path and parse
        filepath = f"resources/{file}.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser()
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()

        # Run alpha Miner
        miner = AlphaMiner()
        miner.run(traces_df)
        loc_csv = miner.get_location_csv()
        trans_csv = miner.get_transition_csv()

        # Read CSV Files from Oracle, sort for comparison
        loc_oracle_df = pd.read_csv(f"resources/{file}-loc-oracle.csv").sort_values(['loc', 'type']).reset_index(drop=True)
        trans_oracle_df = pd.read_csv(f"resources/{file}-trans-oracle.csv").sort_values(['source', 'target', 'type']).reset_index(drop=True)

        # Sort for comparison - StringIO is used to load the csv String into pandas
        loc_actual_df = pd.read_csv(StringIO(loc_csv)).sort_values(['loc', 'type']).reset_index(drop=True)
        trans_actual_df = pd.read_csv(StringIO(trans_csv)).sort_values(['source', 'target', 'type']).reset_index(drop=True)

        # Assert that the result matches
        self.assertEqual(len(loc_oracle_df.compare(loc_actual_df).index), 0)
        self.assertEqual(len(trans_oracle_df.compare(trans_actual_df).index), 0)


if __name__ == '__main__':
    unittest.main()
