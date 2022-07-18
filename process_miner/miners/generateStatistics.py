import timeit

import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class StatisticsGenerator:

    def __init__(self, traces_df, L, logger):
        """
        :param traces_df: pd.DataFrame
        :param L: List
        """
        self.L = L
        self.traces_df = traces_df
        # Sets the colors for the plotly statistics
        pio.templates["ppm"] = go.layout.Template(
            layout_colorway=['#FFC107', '#DB4437', '#2980b9', '#8e44ad', '#2c3e50', '#7f8c8d', '#c0392b']
        )
        pio.templates.default = "ppm"
        self.logger = logger

    def generate_most_common_step(self):
        self.logger.log("Generate Most Common Step Graph")
        start = timeit.default_timer()
        # Generates the most common step statistics and returns it as JSON
        proc_df = self.traces_df[['concept:name']]
        proc_df = proc_df.assign(count=1)
        proc_df = proc_df.groupby("concept:name").sum().reset_index()
        fig = px.bar(proc_df, x="concept:name", y="count")
        graph = pio.to_json(fig)
        end = timeit.default_timer()
        self.logger.log("Generated most common step Graph in " + str(end-start) + "s")
        return graph

    def generate_succession_heatmap(self):
        self.logger.log("Generate Succession Heatmap")
        start = timeit.default_timer()
        # Generates the succession heatmap and returns it as json
        direct_successions_hm = []
        for trace in self.L:
            for i in range(0, len(trace) - 1):
                direct_successions_hm.append((trace[i], trace[i + 1]))

        #print(direct_successions_hm)

        direct_successions_hm_str = []
        for i in direct_successions_hm:
            direct_successions_hm_str.append(i)

        df_successions = pd.DataFrame({'succession': direct_successions_hm_str, 'count': 1})
        df_successions['left'] = df_successions['succession'].transform(lambda x: x[0])
        df_successions['right'] = df_successions['succession'].transform(lambda x: x[1])

        df_successions = df_successions[['left', 'right', 'count']]
        df_successions = df_successions.groupby(['left', 'right']).sum().reset_index()
        #print(df_successions)

        fig = go.Figure(data=go.Heatmap(
            x=df_successions['left'],
            y=df_successions['right'],
            z=df_successions['count'],
            type='heatmap',
            text=df_successions['count'], texttemplate="%{text}",
            textfont={"size": 20},
            colorscale='Inferno'))
        graph = pio.to_json(fig)
        end = timeit.default_timer()
        self.logger.log("Completed Generate Succession Heatmap in " + str(end-start) + "s")
        return graph

    def generate_occurrence_histogram(self):
        self.logger.log("Generate Occurrence Histogram")
        start = timeit.default_timer()
        # Generate occurrence histogram and return as JSON using the ploty histogram function
        if not {'concept:name', 'time:timestamp', 'lifecycle:transition'}.issubset(self.traces_df.columns):
            print("Can't render")
            return ""
        time_df = self.traces_df[['concept:name', 'time:timestamp', 'lifecycle:transition']]
        # time_df['timestamp'] = pd.to_datetime(time_df['time:timestamp'], utc=True)
        fig = px.histogram(time_df, x="time:timestamp", color="concept:name")
        graph = pio.to_json(fig)
        end = timeit.default_timer()
        self.logger.log("Completed Generate Occurrence Histogram in " + str(end-start) + "s")
        return graph

    def generate_average_execution_per_chain_type_over_time(self):
        self.logger.log("Generate average execution per chain type over time")
        start = timeit.default_timer()
        # Generate average execution time per chain over time and return as JSON
        # Mostly some dataframe transformations, that's it
        #print(self.traces_df)
        if not {'concept:name', 'time:timestamp'}.issubset(self.traces_df.columns):
            print("Can't render")
            return ""
        time_df = self.traces_df[['trace_name', 'time:timestamp']]
        # time_df['time:timestamp'] = pd.to_datetime(time_df['time:timestamp'], utc=True)
        time_df = time_df.groupby(['trace_name']).agg(lambda x: (x.max(), x.min())).reset_index()

        time_df['start'] = time_df['time:timestamp'].transform(lambda x: x[0])
        time_df['end'] = time_df['time:timestamp'].transform(lambda x: x[1])
        time_df['delta'] = time_df['start'] - time_df['end']

        l_df = self.traces_df[['trace_name', 'concept:name']]
        l_df = l_df.groupby('trace_name').agg(lambda x: tuple(x))

        time_df = time_df.merge(l_df, on="trace_name")
        # graph = pio.to_json(fig)
        #print(time_df[['concept:name', 'start', 'delta']])

        time_df['delta_sec'] = time_df['delta'].dt.total_seconds().astype(int)
        #time_df.info()
        time_df = time_df[['concept:name', 'start', 'delta_sec']].groupby(['concept:name', 'start']).median().reset_index()

        fig = px.bar(time_df, x="start", y="delta_sec", color="concept:name", width=1600, height=600)
        fig.update_layout(legend=dict(orientation="h")
        )
        graph = pio.to_json(fig)
        end = timeit.default_timer()
        self.logger.log("Completed generate average execution per chain type over time in " + str(end-start) + "s")
        return graph

    def generateTransitionInformation(self):
        self.logger.log("Generate transtion information")
        start = timeit.default_timer()
        # Generate lifecycle:transition information
        result = {}
        for i in self.traces_df['concept:name'].unique():
            filtered_df = self.traces_df[self.traces_df['concept:name'] == i]
            countOccurences = len(filtered_df.index)
            latestOccurence = filtered_df['time:timestamp'].max()
            mostCommonTransition = str(filtered_df['lifecycle:transition'].mode())
            result[i] = {
                'name': i,
                'countOccurence': countOccurences,
                'latestOccurence': latestOccurence,
                'mostCommonTransition': mostCommonTransition
            }
        #print(result)
        end = timeit.default_timer()
        self.logger.log("Completed generate transiton information in " + str(end-start) + "s")
        return result

    def getListOfTransitions(self):
        return list(self.traces_df['lifecycle:transition'].unique())
