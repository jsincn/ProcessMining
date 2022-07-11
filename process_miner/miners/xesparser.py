import timeit
import xml.etree.ElementTree as ET
import pandas as pd
import re

def namespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''



class XESParser:


    def __init__(self):
        self.parsed_logs = pd.DataFrame()

    def read_xes(self, string):
        print("Parsing XES")
        start = timeit.default_timer()
        logs = ET.ElementTree(ET.fromstring(string))
        nmspce = namespace(logs.getroot())

        root = logs.getroot()
        traces = []
        #print(root)
        startConcat = timeit.default_timer()

        for child in root:
            if child.tag == nmspce + "trace":
                traces.append(child)
                #print(child)
        endConcat = timeit.default_timer()
        print("TraceList time " + str(endConcat - startConcat))


        traces_df = pd.DataFrame()
        dataframes = []
        for trace in traces:
            trace_df = pd.DataFrame()
            trace_name = "UNDEFINED"
            event_logs = []
            for tag in trace:
                if tag.tag == nmspce + "string" and tag.attrib["key"] == "concept:name":
                    trace_name = tag.attrib["value"]
                    #print(trace_name)
                if tag.tag == nmspce + "event":
                    event_log = {}
                    for event_prop in tag:
                        event_prop_type = event_prop.get('key')
                        #print(event_prop_type)
                        event_log[event_prop_type] = event_prop.get('value')
                    event_logs.append(event_log)
            trace_df = pd.DataFrame(event_logs)
            trace_df['trace_name'] = trace_name
            dataframes.append(trace_df)

        startConcat = timeit.default_timer()
        traces_df = pd.concat(dataframes)
        print(traces_df['time:timestamp'])
        traces_df.info()
        traces_df['time:timestamp'] = pd.to_datetime(traces_df['time:timestamp'])
        traces_df.info()

        endConcat = timeit.default_timer()
        print("Concat time " + str(endConcat - startConcat))
        if "lifecycle:transition" not in traces_df.columns:
            traces_df["lifecycle:transition"] = "default"
        # traces_df = traces_df.sort_values(["trace_name", "time:timestamp"], ascending=True)

        self.parsed_logs = traces_df
        end = timeit.default_timer()
        print("Completed XES Parsing in " + str(end-start) + "s")
        return True

    def get_parsed_logs(self):
        return self.parsed_logs
