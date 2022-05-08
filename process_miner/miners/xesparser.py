import xml.etree.ElementTree as ET
import pandas as pd


class XESParser:


    def __init__(self):
        self.parsed_logs = pd.DataFrame()

    def read_xes(self, string):
        logs = ET.ElementTree(ET.fromstring(string))

        root = logs.getroot()
        traces = []

        for child in root:
            if child.tag == "{http://www.xes-standard.org/}trace":
                traces.append(child)
                print(child)

        traces_df = pd.DataFrame()
        for trace in traces:
            trace_df = pd.DataFrame()
            trace_name = "UNDEFINED"
            for tag in trace:
                if tag.tag == "{http://www.xes-standard.org/}string" and tag.attrib["key"] == "concept:name":
                    trace_name = tag.attrib["value"]
                    print(trace_name)
                if tag.tag == "{http://www.xes-standard.org/}event":
                    event_log = {}
                    for event_prop in tag:
                        event_prop_type = event_prop.get('key')
                        print(event_prop_type)
                        event_log[event_prop_type] = event_prop.get('value')
                    trace_df = trace_df.append(event_log, ignore_index=True)
            trace_df['trace_name'] = trace_name
            traces_df = traces_df.append(trace_df)

        traces_df = traces_df.sort_values(["trace_name", "time:timestamp"], ascending=True)

        self.parsed_logs = traces_df
        return True

    def get_parsed_logs(self):
        return self.parsed_logs
