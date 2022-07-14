import unittest

from process_miner.logger import Logger
from process_miner.miners.alphaplus import AlphaPlusMiner
from process_miner.miners.xesparser import XESParser
import pandas as pd
from io import StringIO

from tests.utils import utils


class AlphaPlusMinerTests(unittest.TestCase, utils):

    # Main test method
    def test(self):
        testFiles = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7-ap']
        for i in testFiles:
            self.runTest(i)

    # Test runner
    def runTest(self, file):
        # load file from file path and parse
        filepath = f"resources/{file}.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser(Logger())
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()

        # Run alpha Miner
        miner = AlphaPlusMiner()
        miner.run(traces_df)
        loc_csv = miner.get_location_csv()
        trans_csv = miner.get_transition_csv()

        # Read CSV Files from Oracle, sort for comparison
        loc_oracle_df = pd.read_csv(f"resources/{file}-loc-oracle.csv").sort_values(['loc', 'type']).reset_index(drop=True)
        trans_oracle_df = pd.read_csv(f"resources/{file}-trans-oracle.csv").sort_values(['source', 'target', 'type']).reset_index(drop=True)

        # Sort for comparison - StringIO is used to load the csv String into pandas
        loc_actual_df = pd.read_csv(StringIO(loc_csv))
        trans_actual_df = pd.read_csv(StringIO(trans_csv))

        # Sorting of the names is done, as there are sometimes inconsistencies with the order of transitions in splits
        # e.g. a -> b XOR c may be represented by the node abc or acb
        trans_actual_df['source'] = trans_actual_df['source'].map(lambda a: "".join(sorted(a)))
        trans_actual_df['target'] = trans_actual_df['target'].map(lambda a: "".join(sorted(a)))
        trans_actual_df = trans_actual_df.sort_values(['source', 'target', 'type']).reset_index(drop=True)
        loc_actual_df['loc'] = loc_actual_df['loc'].map(lambda a: "".join(sorted(a)))
        loc_actual_df = loc_actual_df.sort_values(['loc', 'type']).reset_index(drop=True)

        trans_oracle_df['source'] = trans_oracle_df['source'].map(lambda a: "".join(sorted(a)))
        trans_oracle_df['target'] = trans_oracle_df['target'].map(lambda a: "".join(sorted(a)))
        trans_oracle_df = trans_oracle_df.sort_values(['source', 'target', 'type']).reset_index(drop=True)
        loc_oracle_df['loc'] = loc_oracle_df['loc'].map(lambda a: "".join(sorted(a)))
        loc_oracle_df = loc_actual_df.sort_values(['loc', 'type']).reset_index(drop=True)

        # Assert that the result matches
        self.assertEqual(len(loc_oracle_df.compare(loc_actual_df).index), 0, "Failed on location oracle with file "
                                                                                + file)
        self.assertEqual(len(trans_oracle_df.compare(trans_actual_df).index), 0, "Failed on transition oracle with "
                                                                                 "file " + file)


if __name__ == '__main__':
    unittest.main()
