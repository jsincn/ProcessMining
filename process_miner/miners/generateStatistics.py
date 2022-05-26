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
            layout_colorway=['#FFC107', '#DB4437', '#F4B400']
        )
        pio.templates.default = "ppm"

    def generate_most_common_step(self):
        proc_df = self.traces_df[['concept:name']]
        proc_df = proc_df.assign(count=1)
        proc_df = proc_df.groupby("concept:name").sum().reset_index()
        proc_df.head(10)
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
            text=df_successions['count'],texttemplate="%{text}",
                    textfont={"size":20},
            colorscale='Inferno'))
        graph = pio.to_json(fig)
        return graph
