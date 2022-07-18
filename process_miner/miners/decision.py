import timeit

import pandas as pd

def is_all_equal(series):
    num_arr = series.to_numpy()
    return (num_arr[0] == num_arr).all()

class DecisionMiner:

    def __init__(self, traces_df, L, logger):
        self.L_EXTENDED = None
        self.traces_df = traces_df
        self.L = L
        self.logger = logger

    def calculateDecision(self):
        self.logger.log("Running decision calculation")
        start = timeit.default_timer()
        trace_names = self.traces_df.trace_name.unique()
        self.traces_df = self.traces_df.fillna(0)
        self.L_EXTENDED = []
        for trace_name in trace_names:
            trace = self.traces_df[self.traces_df.trace_name == trace_name]
            self.L_EXTENDED.append(trace)

        direct_successions_hm = []
        for trace in self.L_EXTENDED:
            for i in range(0, len(trace.index) - 1):
                direct_successions_hm.append((trace.iloc[[i, i+1]]))

        # Generate a dict of dataframes for each succession
        # Each Dataframe has 2 Rows, the original transition and the following transition
        ds_helper = {}
        for ds in direct_successions_hm:
            first_activity = ds.loc[ds.index[0],'concept:name']
            if first_activity not in ds_helper.keys():
                ds_helper[first_activity] = {}
                ds_helper[first_activity]['options'] = set()
                ds_helper[first_activity]['dataFrames'] = []
            ds_helper[first_activity]['options'].add(ds.loc[ds.index[1], 'concept:name'])
            ds_helper[first_activity]['dataFrames'].append(ds)

        # Final calculation of decision information
        # Assumptions made:
        # - The attribute that correlates with the selection of A or B as the following decision is equal among all
        #   these successions
        # - The attribute that causes the difference is the same among the the two possible successions
        # - Only the attributes of the preceding event are considered
        # Example: A -> B XOR C
        #  Trace 1: (A, name=Mary, cost=400) -> (B, name=Mary, cost=300)
        #  Trace 2: (A, name=Mary, cost=400) -> (B, name=Mary, cost=213)
        #  Trace 3: (A, name=Sarah, cost=100) -> (C, name=Mary, cost=123)
        #  Trace 4: (A, name=John, cost=100) -> (C, name=Mary, cost=671)
        #  1. Cost and Name in Events C and B are not considered, as this information is 'unknown' during the decision
        #  2. Name is not considered, as the value of name is not consistent every time C is chosen
        #  3. The Attribute cost is considered as being responsible for the selection as it is correlates with B or C
        # Limitations:
        # - No calculation of bounds (i.e. cost < 100)
        # - Anomalies in large traces can cause the real factor to be missed,
        #   as there are currently no thresholds implemented
        # - More complex decisions are difficult to detect, especially if there are more than 1 choices to make
        # I also did some testing with decision trees, but was unable to get reasonable results during my initial
        # testing, due to complications arising from the discretisation of the values

        result = {}
        for first_activity in ds_helper.keys():
            result[first_activity] = {}
            result[first_activity]['options'] = {}
            for option in ds_helper[first_activity]['options']:
                options_df = pd.DataFrame()
                result[first_activity]['options'][option] = {}
                result[first_activity]['options'][option]['equals'] = {}
                result[first_activity]['options'][option]['notequals'] = {}
                for df in ds_helper[first_activity]['dataFrames']:
                    #print(df.loc[df.index[1], 'concept:name'])
                    if df.loc[df.index[1], 'concept:name'] == option:
                        options_df = pd.concat([options_df, df.iloc[[0]]])
                # print(options_df)
                for col in options_df.columns:
                    if is_all_equal(options_df[col]):
                        result[first_activity]['options'][option]['equals'][col] = options_df[col].to_numpy()[0]
                    else:
                        result[first_activity]['options'][option]['notequals'][col] = options_df[col].to_numpy()[0]
            common_attributes = set()
            for option in result[first_activity]['options']:
                if len(common_attributes) > 0:
                    common_attributes = common_attributes.intersection(result[first_activity]['options'][option]['equals'].keys())
                else:
                    common_attributes = set(result[first_activity]['options'][option]['equals'].keys())
            result[first_activity]['commonAttributes'] = list(common_attributes)
        end = timeit.default_timer()
        self.logger.log("Completed decision calculation in " + str(end-start) + " s")
        return result

