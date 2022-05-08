import pandas as pd
from itertools import chain, combinations
import itertools


def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def jointuple(tpl, sep="", lbr="", rbr=""):
    return sep.join(lbr + jointuple(x) + rbr if isinstance(x, tuple) else str(x) for x in tpl)


class AlphaMiner:
    def __init__(self):
        self.L = []
        self.FL = []
        self.TL = []
        self.TI = []
        self.TO = []
        self.XL = []
        self.YL = []
        self.combinations = []

    def run(self, traces_df):
        trace_names = traces_df.trace_name.unique()
        self.L = []
        for trace_name in trace_names:
            trace = traces_df[traces_df.trace_name == trace_name]
            trace_concept_name = trace['concept:name']
            self.L.append(tuple(trace_concept_name))

        # Prepare Groups
        direct_successions = []
        for trace in self.L:
            for i in range(0, len(trace) - 1):
                if (trace[i], trace[i + 1]) not in direct_successions:
                    direct_successions.append((trace[i], trace[i + 1]))

        causalities = []
        for succession in direct_successions:
            if (succession[1], succession[0]) not in direct_successions:
                causalities.append(succession)

        parallels = []
        for succession in direct_successions:
            if (succession[1], succession[0]) in direct_successions:
                parallels.append(succession)

        choices = []
        alphabet = traces_df["concept:name"].unique()
        for a in alphabet:
            for b in alphabet:
                if (a, b) not in direct_successions and (b, a) not in direct_successions:
                    choices.append((a, b))
                    if b != a:
                        choices.append((b, a))

        # Algorithm Step 1-3
        self.TL = list(alphabet)
        self.TI = []
        for i in self.L:
            self.TI.append(i[0])
        self.TI = list(set(self.TI))
        self.TO = []
        for i in self.L:
            self.TO.append(i[len(i) - 1])
        self.TO = list(set(self.TO))

        side_combinations = list(powerset(alphabet))
        self.combinations = list(itertools.product(side_combinations, side_combinations))

        for combination in self.combinations:
            A = combination[0]
            B = combination[1]
            valid = True
            if len(A) == 0 or len(B) == 0:
                # print ("EMPTY SET")
                valid = False
            for a in A:
                for b in B:
                    if (a, b) not in causalities:
                        # print ("NO Causality", end="")
                        valid = False
            for a1 in A:
                for a2 in A:
                    if (a1, a2) not in choices:
                        valid = False
            for b1 in B:
                for b2 in B:
                    if (b1, b2) not in choices:
                        valid = False
            if valid:
                self.XL.append((A, B))

        for combination in self.XL:
            valid = True
            for comparison in self.XL:

                if set(combination[0]).issubset(comparison[0]) and set(combination[1]).issubset(comparison[1]):
                    if combination != comparison:
                        valid = False
                        break
            if valid:
                self.YL.append(combination)

        for combination in self.YL:
            # print(combination)
            for a in combination[0]:
                self.FL.append((a, combination))

            for b in combination[1]:
                self.FL.append((combination, b))

        for start in self.TI:
            self.FL.append(("Start", start))

        for end in self.TO:
            self.FL.append((end, "End"))
        self.TL.append("Start")
        self.TL.append("End")

    def get_location_csv(self):
        csv = "loc,type\n"
        for t in self.TL:
            if t == "Start" or t == "End":
                csv = csv + t + ",se\n"
            else:
                csv = csv + t + ",trans\n"
        for y in self.YL:
            csv = csv + jointuple(y) + ",pos\n"
        return csv

    def get_transition_csv(self):
        csv = "source,target,type\n"
        for f in self.FL:
            csv = csv + jointuple(f[0]) + "," + jointuple(f[1]) + ",all\n"
        return csv

    def get_meta(self):
        meta = {'possibilities': {'value': len(self.combinations), 'name': "Combinations for XL"}}
        return meta
