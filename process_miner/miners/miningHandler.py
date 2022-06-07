import timeit
from datetime import datetime

from werkzeug.utils import secure_filename

from process_miner.miners.alpha import AlphaMiner
from process_miner.miners.generateStatistics import StatisticsGenerator
from process_miner.miners.heuristic import HeuristicMiner
from process_miner.miners.xesparser import XESParser


class MiningHandler:

    def __init__(self, algorithm, file, lifecycleTransition):
        self.miner = None
        self.file = file
        self.algorithm = algorithm
        self.success = False
        self.stop = 0
        self.start = 0
        self.stats = None
        self.lifecycleTransition = lifecycleTransition

    def run(self):
        # runs the algorithm
        if self.algorithm == "Alpha Miner":
            self.start = timeit.default_timer()
            parser = XESParser()
            if parser.read_xes(self.file.read()):
                traces_df = parser.get_parsed_logs()
                # filter lifecycle transition
                if self.lifecycleTransition != "":
                    traces_df = traces_df[traces_df['lifecycle:transition'] == self.lifecycleTransition]
                self.miner = AlphaMiner()
                self.miner.run(traces_df)
                self.stop = timeit.default_timer()
                self.stats = StatisticsGenerator(traces_df, self.miner.L)
                self.success = True
        elif self.algorithm == "Heuristic Miner":
            # Run the Heuristic Miner
            self.start = timeit.default_timer()
            parser = XESParser()
            if parser.read_xes(self.file.read()):
                traces_df = parser.get_parsed_logs()
                # filter lifecycle transition
                if self.lifecycleTransition != "":
                    traces_df = traces_df[traces_df['lifecycle:transition'] == self.lifecycleTransition]
                self.miner = HeuristicMiner()
                self.miner.run(traces_df)
                self.stop = timeit.default_timer()
                self.stats = StatisticsGenerator(traces_df, self.miner.L)
                self.success = True

    def prepare_response(self):
        if self.algorithm == "Alpha Miner":
            response = {'locations': self.miner.get_location_csv(), 'transitions': self.miner.get_transition_csv(),
                        'filename': secure_filename(self.file.filename), 'runtime': self.stop - self.start,
                        'algorithm': "Alpha Miner", 'cache': False, 'timestamp': datetime.now(),
                        'mostCommonStep': self.stats.generate_most_common_step(),
                        'successionHeatmap': self.stats.generate_succession_heatmap(),
                        'nodeStats': self.stats.generateTransitionInformation(),
                        'meta': self.miner.get_meta()}
            return response
        elif self.algorithm == "Heuristic Miner":
            response = {'successionMatrix': self.miner.get_succession_matrix(),
                        'dependencyMeasureMatrix': self.miner.get_dependency_measure_matrix(),
                        'alphabet': self.miner.get_alphabet(),
                        'start': self.miner.get_start(),
                        'end': self.miner.get_end(),
                        'maxOccurrences': self.miner.get_max_occurrences(),
                        'filename': secure_filename(self.file.filename), 'runtime': self.stop - self.start,
                        'algorithm': "Heuristic Miner", 'cache': False, 'timestamp': datetime.now(),
                        'mostCommonStep': self.stats.generate_most_common_step(),
                        'successionHeatmap': self.stats.generate_succession_heatmap(),
                        'nodeStats': self.stats.generateTransitionInformation(),
                        'meta': self.miner.get_meta()}
            return response
