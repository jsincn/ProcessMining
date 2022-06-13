from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


class StatisticsGenerator:

    def __init__(self, traces_df, L):
        self.L = L
        self.traces_df = traces_df
        pio.templates["ppm"] = go.layout.Template(
            layout_colorway=['#FFC107', '#DB4437', '#2980b9', '#8e44ad', '#2c3e50', '#7f8c8d', '#c0392b']
        )
        pio.templates.default = "ppm"

    def generate_most_common_step(self):
        proc_df = self.traces_df[['concept:name']]
        proc_df = proc_df.assign(count=1)
        proc_df = proc_df.groupby("concept:name").sum().reset_index()
        fig = px.bar(proc_df, x="concept:name", y="count")
        graph = pio.to_json(fig)
        return graph

    def generate_succession_heatmap(self):
        direct_successions_hm = []
        for trace in self.L:
            for i in range(0, len(trace) - 1):
                direct_successions_hm.append((trace[i], trace[i + 1]))

        print(direct_successions_hm)

        direct_successions_hm_str = []
        for i in direct_successions_hm:
            direct_successions_hm_str.append(i)

        df_successions = pd.DataFrame({'succession': direct_successions_hm_str, 'count': 1})
        df_successions['left'] = df_successions['succession'].transform(lambda x: x[0])
        df_successions['right'] = df_successions['succession'].transform(lambda x: x[1])

        df_successions = df_successions[['left', 'right', 'count']]
        df_successions = df_successions.groupby(['left', 'right']).sum().reset_index()
        print(df_successions)

        fig = go.Figure(data=go.Heatmap(
            x=df_successions['left'],
            y=df_successions['right'],
            z=df_successions['count'],
            type='heatmap',
            text=df_successions['count'], texttemplate="%{text}",
            textfont={"size": 20},
            colorscale='Inferno'))
        graph = pio.to_json(fig)
        return graph

    def generate_occurrence_histogram(self):
        if not {'concept:name', 'time:timestamp', 'lifecycle:transition'}.issubset(self.traces_df.columns):
            print("Can't render")
            # fig = px.bar(proc_df, x="concept:name", y="count")
            # graph = pio.to_json(fig)
            # return graph
        time_df = self.traces_df[['concept:name', 'time:timestamp', 'lifecycle:transition']]
        time_df['timestamp'] = pd.to_datetime(time_df['time:timestamp'])
        fig = px.histogram(time_df, x="time:timestamp", color="concept:name")
        graph = pio.to_json(fig)
        return graph

    def generate_average_execution_per_chain_type_over_time(self):
        if not {'concept:name', 'time:timestamp'}.issubset(self.traces_df.columns):
            print("Can't render")
            # fig = px.bar(proc_df, x="concept:name", y="count")
            # graph = pio.to_json(fig)
            # return graph
        # Average execution time per chain type over time
        time_df = self.traces_df[['trace_name', 'time:timestamp']]
        time_df['time:timestamp'] = pd.to_datetime(time_df['time:timestamp'])
        time_df = time_df.groupby(['trace_name']).agg(lambda x: (x.max(), x.min())).reset_index()

        time_df['start'] = time_df['time:timestamp'].transform(lambda x: x[0])
        time_df['end'] = time_df['time:timestamp'].transform(lambda x: x[1])
        time_df['delta'] = time_df['start'] - time_df['end']

        l_df = self.traces_df[['trace_name', 'concept:name']]
        l_df = l_df.groupby('trace_name').agg(lambda x: tuple(x))

        time_df = time_df.merge(l_df, on="trace_name")
        # graph = pio.to_json(fig)
        time_df = time_df[['concept:name', 'start', 'delta']].groupby(['concept:name', 'start']).median().reset_index()
        time_df['delta_sec'] = time_df['delta'].dt.total_seconds()

        # Create layout. With layout you can customize plotly plo
        fig = px.bar(time_df, x="start", y="delta_sec", color="concept:name")
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
        graph = pio.to_json(fig)
        return graph

    def generateTransitionInformation(self):
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
        print(result)
        return result
