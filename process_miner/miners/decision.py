import timeit
from pprint import pprint

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

        ds_helper = {}
        for ds in direct_successions_hm:
            first_activity = ds.loc[ds.index[0],'concept:name']
            if first_activity not in ds_helper.keys():
                ds_helper[first_activity] = {}
                ds_helper[first_activity]['options'] = set()
                ds_helper[first_activity]['dataFrames'] = []
            ds_helper[first_activity]['options'].add(ds.loc[ds.index[1], 'concept:name'])
            ds_helper[first_activity]['dataFrames'].append(ds)
        #print(ds_helper)

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
        self.logger.log("Completed decision calculation in " + str(end-start) + "s")
        return result

