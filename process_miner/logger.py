

class Logger:

    def __init__(self):
        self.logs = []

    def log(self, string):
        self.logs.append(str(string))

    def get_logs(self):
        self.logs.append("Done!")
        return "<br>".join(self.logs)