import unittest

from process_miner.logger import Logger
from process_miner.miners.xesparser import XESParser


class TestXesParser(unittest.TestCase):
    def testL1(self):
        filepath = "resources/L1.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser(Logger())
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()
        l = self.generate_l(traces_df)
        oracle_dict = [
            (('a', 'b', 'c', 'd'), 3),
            (('a', 'c', 'b', 'd'), 2),
            (('a', 'e', 'd'), 1),
        ]
        oracle = self.generate_oracle(oracle_dict)
        oracle.sort()
        l.sort()
        self.assertEqual(l, oracle)

    def testL2(self):
        filepath = "resources/L2.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser(Logger())
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()
        l = self.generate_l(traces_df)
        oracle_dict = [
            (('a', 'b', 'c', 'd'), 3),
            (('a', 'c', 'b', 'd'), 4),
            (('a', 'b', 'c', 'e', 'f', 'b', 'c', 'd'), 2),
            (('a', 'b', 'c', 'e', 'f', 'c', 'b', 'd'), 1),
            (('a', 'c', 'b', 'e', 'f', 'b', 'c', 'd'), 2),
            (('a', 'c', 'b', 'e', 'f', 'b', 'c', 'e', 'f', 'c', 'b', 'd'), 1),
        ]
        oracle = self.generate_oracle(oracle_dict)
        oracle.sort()
        l.sort()
        self.assertEqual(l, oracle)

    def testL3(self):
        filepath = "resources/L3.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser(Logger())
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()
        l = self.generate_l(traces_df)
        oracle_dict = [
            (('a', 'b', 'c', 'd', 'e', 'f', 'b', 'd', 'c', 'e', 'g'), 1),
            (('a', 'b', 'c', 'd', 'e', 'f', 'b', 'c', 'd', 'e', 'f', 'b', 'd', 'c', 'e', 'g'), 1),
            (('a', 'b', 'd', 'c', 'e', 'g'), 2)
        ]
        oracle = self.generate_oracle(oracle_dict)
        oracle.sort()
        l.sort()
        self.assertEqual(l, oracle)

    def testL4(self):
        filepath = "resources/L4.xes"
        test_xml_string = self.load_test_file(filepath)
        parser = XESParser(Logger())
        parser.read_xes(test_xml_string)
        traces_df = parser.get_parsed_logs()
        l = self.generate_l(traces_df)
        oracle_dict = [
            (tuple('acd'), 45),
            (tuple('bcd'), 42),
            (tuple('ace'), 38),
            (tuple('bce'), 22)
        ]
        oracle = self.generate_oracle(oracle_dict)
        oracle.sort()
        l.sort()
        self.assertEqual(l, oracle)

    @staticmethod
    def load_test_file(filepath):
        f = open(filepath, "r")
        test_xml_string = f.read()
        f.close()
        return test_xml_string

    @staticmethod
    def generate_oracle(oracle_dict):
        oracle = []
        for i in oracle_dict:
            for j in range(0, i[1]):
                oracle.append(i[0])
        return oracle

    @staticmethod
    def generate_l(traces_df):
        trace_names = traces_df.trace_name.unique()
        l = []
        for trace_name in trace_names:
            trace = traces_df[traces_df.trace_name == trace_name]
            trace_concept_name = trace['concept:name']
            l.append(tuple(trace_concept_name))
        return l


if __name__ == '__main__':
    unittest.main()
