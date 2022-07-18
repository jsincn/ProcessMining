from itertools import chain, combinations
import itertools

def powerset(iterable: object) -> object:
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    :param iterable:
    :return:
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def jointuple(tpl, sep="", lbr="", rbr=""):
    """
    Used to generate names for places by joining the affected transition names
    Based on https://stackoverflow.com/questions/47795792/how-to-deep-join-a-tuple-into-a-string
    :param tpl: Tuple
    :param sep: Char of separator that may be added
    :param lbr: Left bracket optional
    :param rbr: Right bracket optional
    :return: String
    """
    return sep.join(lbr + jointuple(x) + rbr if isinstance(x, tuple) else str(x) for x in tpl)


class AlphaPlusMiner:
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

        ### PREPROCESSING FOR ALPHA PLUS MINER
        # Based on https://docs.google.com/document/d/1JtuECbGZ3DusNpmBZhXeq8R_UPCRU5V7NG8GL17h1aA/pub BPMProject and
        # https://github.com/eadordzhiev/AlphaPlusAlgorithm/blob/master/AlphaMinerTest1/AlphaMiner.cs

        # Remove all loops of length 1
        # Identify loop 1 transitions
        direct_successions_dash = []
        loop1 = []
        l_1_l = {}
        for trans in direct_successions:
            if trans[0] != trans[1]:
                direct_successions_dash.append(trans)
            else:
                loop1.append(trans)

        #print(direct_successions_dash)
        #print(loop1)

        # Recalculate transitions without the loop 1 transitions
        # Create l_1_l list that holds all relevant information for each loop of length 1
        # Used for adding in the loop again at the end
        direct_successions = []
        for l in loop1:
            l_1_l[l[0]] = {}
            l_1_l[l[0]]['activity'] = l[0]
            l_1_l[l[0]]['before'] = []
            l_1_l[l[0]]['after'] = []
            for trans in direct_successions_dash:
                if l[0] == trans[1]:
                    l_1_l[l[0]]['before'].append(trans[0])
                elif l[0] == trans[0]:
                    l_1_l[l[0]]['after'].append(trans[1])
                else:
                    direct_successions.append(trans)
        if len(loop1) < 1:
            for trans in direct_successions_dash:
                direct_successions.append(trans)

        # calculate subsequence aba: a △ b ⟺ ...aba... exists
        subsequence = []
        for trace in self.L:
            for i in range(len(trace) - 2):
                if trace[i] == trace[i + 2]:
                    subsequence.append((trace[i], trace[i + 1]))
        subsequence = list(set(subsequence))

        # calculate subsequence aba and bab: a ♢ b ⟺ ...aba... and ...bab... exist
        both_sequence = []
        for (a, b) in subsequence:
            if (b, a) in subsequence:
                both_sequence.append((a, b))

        # Different Causality and Parallel calculation
        causalities = []
        for succession in direct_successions:
            if (succession[1], succession[0]) not in direct_successions or (succession[1], succession[0]) in both_sequence:
                causalities.append(succession)

        parallels = []
        for succession in direct_successions:
            if (succession[1], succession[0]) in direct_successions and (succession[0], succession[1]) not in both_sequence:
                parallels.append(succession)

        ### END OF PREPROCESSING FOR ALPHA PLUS MINER

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


        # Find XL (Step 4)
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

        # Find YL (Step 5)
        for combination in self.XL:
            valid = True
            for comparison in self.XL:

                if set(combination[0]).issubset(comparison[0]) and set(combination[1]).issubset(comparison[1]):
                    if combination != comparison:
                        valid = False
                        break
            if valid:
                self.YL.append(combination)

        # PL (Step 6) is omitted here, as that is done during CSV Creation

        # Find FL (Step 7)
        for combination in self.YL:
            # print(combination)
            for a in combination[0]:
                self.FL.append((a, combination))
            for b in combination[1]:
                self.FL.append((combination, b))

        ## POST PROCESSING FOR ALPHA PLUS MINER
        # For each loop of length 1
        for e in l_1_l:
            element = l_1_l[e]
            index = -1
            # Identify the place to 'dock onto' - i.e. the place where we removed the length 1 loop from
            for i, item in enumerate(self.XL):
                if element['before'][0] in item[0] and element['after'][0] in item[1]:
                    index = i
                    break
            if index == -1:
                continue
            else:
                # Add arcs at the correct position to reattach our loop 1 transition
                self.FL.append((element['activity'], self.XL[index]))
                self.FL.append((self.XL[index], element['activity']))
        ## END POST PROCESSING FOR ALPHA PLUS MINER

        # Add start transitions
        for start in self.TI:
            self.FL.append(("Start", start))
        for end in self.TO:
            self.FL.append((end, "End"))
        # Add start places
        self.TL.append("Start")
        self.TL.append("End")

    def get_location_csv(self):
        """
        Generates a csv string of the locations
        :return:
        """
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
        """
        Generates a csv string of the transitions
        :return: String
        """
        csv = "source,target,type\n"
        for f in self.FL:
            csv = csv + jointuple(f[0]) + "," + jointuple(f[1]) + ",all\n"
        return csv

    def get_transition_list(self):
        transitions = []
        for f in self.FL:
            transitions.append([jointuple(f[0]), jointuple(f[1])])
        return transitions

    def get_meta(self):
        """
        Generates meta data about the algorithm execution
        :return: dict
        """
        meta = {'possibilities': {'value': len(self.combinations), 'name': "Combinations for XL"}}
        return meta
