import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


class HeuristicMiner:

    def __init__(self):
        self.TI = []
        self.TO = []
        self.L = []
        self.alphabet = []
        self.succession_matrix = pd.DataFrame()
        self.dependency_measure_matrix = pd.DataFrame()
        self.and_xor_split_matrix = pd.DataFrame()

    def run(self, traces_df):
        trace_names = traces_df.trace_name.unique()
        self.alphabet = traces_df["concept:name"].unique()

        # Calculate L
        self.L = []
        for trace_name in trace_names:
            trace = traces_df[traces_df.trace_name == trace_name]
            trace_concept_name = trace['concept:name']
            # Appending a tuple may seem weird, but trace['concept:name'] is actually a series of the column values
            # in the Dataframe
            self.L.append(tuple(trace_concept_name))

        # Calculate direct successions
        direct_successions = []
        for trace in self.L:
            for i in range(0, len(trace) - 1):
                direct_successions.append((trace[i], trace[i + 1]))

        #Create an empty row for further use (adding missing rows to the succession matrix)
        empty_row = []
        for i in self.alphabet:
            empty_row.append(0)

        # Calculate the succession matrix
        # Create new dataframe
        df_successions = pd.DataFrame({'succession': direct_successions, 'count': 1})
        # Split the succession tuple into two columns
        df_successions['left'] = df_successions['succession'].transform(lambda x: x[0])
        df_successions['right'] = df_successions['succession'].transform(lambda x: x[1])
        # Remove unnecessary columns
        df_successions = df_successions[['left', 'right', 'count']]
        # Group and sum the successions
        df_successions = df_successions.groupby(["left", "right"]).sum().reset_index()
        # Convert to int to prevent issues down the line
        df_successions['count'] = df_successions['count'].astype(int)
        # Pivot to turn it into a matrix
        self.succession_matrix = df_successions.pivot(index='left', columns='right', values='count')
        # Fillna(0) in order to prevent comparison issues when the value is 0
        self.succession_matrix = self.succession_matrix.fillna(0)

        # Fill missing values in the succession matrix
        for r in self.alphabet:
            if r not in self.succession_matrix.columns:
                self.succession_matrix[r] = 0

        for l in self.alphabet:
            if l not in self.succession_matrix.index:
                self.succession_matrix.loc[l] = empty_row

        # calculate dependency measure matrix and and_xor_split values
        dependency_measures_df = pd.DataFrame(columns=['left', 'right', 'val'])
        and_xor_split_df = pd.DataFrame(columns=['left', 'right', 'val'])
        df_s = self.succession_matrix
        for l in self.alphabet:
            for r in self.alphabet:
                if l != r:
                    val_dependency = (abs(df_s.loc[l][r]) - abs(df_s.loc[r][l])) / (
                                abs(df_s.loc[l][r]) + abs(df_s.loc[r][l]) + 1)
                    val_and_xor = (abs(df_s.loc[l][r]) + abs(df_s.loc[r][l])) / (
                                abs(df_s.loc[l][r]) + abs(df_s.loc[r][l]) + 1)
                    # print(l + r + str(val))
                    dependency_measures_df = dependency_measures_df.append(
                        {'left': l, 'right': r, 'val': val_dependency},
                        ignore_index=True)
                    and_xor_split_df = and_xor_split_df.append({'left': l, 'right': r, 'val': val_and_xor},
                                                               ignore_index=True)
                else:
                    val = abs(df_s.loc[l][r]) / (abs(df_s.loc[l][r]) + 1)
                    dependency_measures_df = dependency_measures_df.append({'left': l, 'right': r, 'val': val},
                                                                           ignore_index=True)
                    and_xor_split_df = and_xor_split_df.append({'left': l, 'right': r, 'val': -1},
                                                               ignore_index=True)

        dependency_measures_df = dependency_measures_df.reset_index()
        and_xor_split_df = and_xor_split_df.reset_index()
        # Again PIVOT to make it easy to use afterwards
        self.dependency_measure_matrix = dependency_measures_df.pivot(index="left", columns='right', values='val')
        self.and_xor_split_matrix = and_xor_split_df.pivot(index="left", columns='right', values='val')

        # Set TI and TO
        for i in self.L:
            self.TI.append(i[0])
        self.TI = list(set(self.TI))
        for i in self.L:
            self.TO.append(i[len(i) - 1])
        self.TO = list(set(self.TO))

    def get_l(self):
        return self.L

    def get_succession_matrix(self):
        return self.succession_matrix.to_dict('index')

    def get_dependency_measure_matrix(self):
        return self.dependency_measure_matrix.to_dict('index')

    def get_and_xor_split_matrix(self):
        return self.and_xor_split_matrix.to_dict('index')

    def get_alphabet(self):
        return list(self.alphabet)

    def get_meta(self):
        meta = {'process_nodes': {'value': len(self.alphabet), 'name': "Number of process nodes"}}
        return meta

    def get_start(self):
        return list(self.TI)

    def get_end(self):
        return list(self.TO)

    def get_max_occurrences(self):
        # Used for setting the max value on the slider
        tmp = self.succession_matrix.melt()
        return tmp['value'].max()
