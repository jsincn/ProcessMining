import timeit
from datetime import datetime

from werkzeug.utils import secure_filename

from process_miner.logger import Logger
from process_miner.miners.alpha import AlphaMiner
from process_miner.miners.alphaplus import AlphaPlusMiner
from process_miner.miners.decision import DecisionMiner
from process_miner.miners.generateStatistics import StatisticsGenerator
from process_miner.miners.heuristic import HeuristicMiner
from process_miner.miners.xesparser import XESParser


class MiningHandler:

    def __init__(self, algorithm, file, lifecycleTransition):
        self.decisions = None
        self.miner = None
        self.file = file
        self.algorithm = algorithm
        self.success = False
        self.stop = 0
        self.start = 0
        self.stats = None
        self.lifecycleTransition = lifecycleTransition
        self.logger = Logger()

    def run(self):
        # runs the algorithm
        self.start = timeit.default_timer()
        if self.algorithm == "Alpha Miner":
            parser = XESParser(self.logger)
            if parser.read_xes(self.file.read()):
                traces_df = parser.get_parsed_logs()
                # filter lifecycle transition
                if self.lifecycleTransition != "":
                    traces_df = traces_df[traces_df['lifecycle:transition'] == self.lifecycleTransition]
                self.logger.log("Starting Alpha Miner")
                minerStart = timeit.default_timer()
                self.miner = AlphaMiner()
                self.miner.run(traces_df)
                minerStop = timeit.default_timer()
                self.logger.log("Completed alpha miner in " + str(minerStop-minerStart) + "s")
                self.stats = StatisticsGenerator(traces_df, self.miner.L, self.logger)
                self.decisions = DecisionMiner(traces_df, self.miner.L, self.logger)
                self.success = True
        elif self.algorithm == "Alpha Plus Miner":
            parser = XESParser(self.logger)
            if parser.read_xes(self.file.read()):
                traces_df = parser.get_parsed_logs()
                # filter lifecycle transition
                if self.lifecycleTransition != "":
                    traces_df = traces_df[traces_df['lifecycle:transition'] == self.lifecycleTransition]
                self.logger.log("Starting Alpha Plus Miner")
                minerStart = timeit.default_timer()
                self.miner = AlphaPlusMiner()
                self.miner.run(traces_df)
                minerStop = timeit.default_timer()
                self.logger.log("Completed alpha plus miner in " + str(minerStop-minerStart) + "s")
                self.stats = StatisticsGenerator(traces_df, self.miner.L, self.logger)
                self.decisions = DecisionMiner(traces_df, self.miner.L, self.logger)
                self.success = True
        elif self.algorithm == "Heuristic Miner":
            # Run the Heuristic Miner
            parser = XESParser(self.logger)
            if parser.read_xes(self.file.read()):
                traces_df = parser.get_parsed_logs()
                # filter lifecycle transition
                if self.lifecycleTransition != "":
                    traces_df = traces_df[traces_df['lifecycle:transition'] == self.lifecycleTransition]
                self.logger.log("Starting Heuristic Miner")
                minerStart = timeit.default_timer()
                self.miner = HeuristicMiner()
                self.miner.run(traces_df)
                minerStop = timeit.default_timer()
                self.logger.log("Completed heuristic miner in " + str(minerStop-minerStart) + "s")
                self.stats = StatisticsGenerator(traces_df, self.miner.L, self.logger)
                self.decisions = DecisionMiner(traces_df, self.miner.L, self.logger)
                self.success = True

    def prepare_response(self):
        if self.algorithm == "Alpha Miner" or self.algorithm == "Alpha Plus Miner":
            response = {'locations': self.miner.get_location_csv(), 'transitions': self.miner.get_transition_csv(),
                        'filename': secure_filename(self.file.filename),
                        'algorithm': self.algorithm, 'cache': False, 'timestamp': datetime.now(),
                        'mostCommonStep': self.stats.generate_most_common_step(),
                        'successionHeatmap': self.stats.generate_succession_heatmap(),
                        'occurrenceHistogram': self.stats.generate_occurrence_histogram(),
                        'listLifecycleTransitions': self.stats.getListOfTransitions(),
                        'averageExecutionChainTypeTime': self.stats.generate_average_execution_per_chain_type_over_time(),
                        'nodeStats': self.stats.generateTransitionInformation(),
                        'meta': self.miner.get_meta(),
                        'transitionList': self.miner.get_transition_list(),
                        'decisionInformation': self.decisions.calculateDecision(),
                        'logs': self.logger.get_logs()}
            self.stop = timeit.default_timer()
            response['runtime'] = self.stop - self.start
            return response
        elif self.algorithm == "Heuristic Miner":
            response = {'successionMatrix': self.miner.get_succession_matrix(),
                        'dependencyMeasureMatrix': self.miner.get_dependency_measure_matrix(),
                        'andXorMeasureMatrix': self.miner.get_and_xor_split_matrix(),
                        'alphabet': self.miner.get_alphabet(),
                        'start': self.miner.get_start(),
                        'end': self.miner.get_end(),
                        'maxOccurrences': 100,
                        'filename': secure_filename(self.file.filename),
                        'algorithm': "Heuristic Miner", 'cache': False, 'timestamp': datetime.now(),
                        'l': self.miner.get_l(),
                        'mostCommonStep': self.stats.generate_most_common_step(),
                        'successionHeatmap': self.stats.generate_succession_heatmap(),
                        'occurrenceHistogram': self.stats.generate_occurrence_histogram(),
                        'listLifecycleTransitions': self.stats.getListOfTransitions(),
                        'averageExecutionChainTypeTime': self.stats.generate_average_execution_per_chain_type_over_time(),
                        'nodeStats': self.stats.generateTransitionInformation(),
                        'meta': self.miner.get_meta(),
                        'decisionInformation': self.decisions.calculateDecision(),
                        'logs': self.logger.get_logs()}
            self.stop = timeit.default_timer()
            response['runtime'] = self.stop - self.start
            return response
