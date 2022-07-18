class Logger:

    def __init__(self):
        self.logs = []
        self.errorMessages = {
            "emptyTraceDF": "Trace Dataframe empty after parsing: Check if lifecycle.transition correct! Lifecycle Transition \"",
            "errorDuringErrorLogging": "An error occured, but the error code. However during logging another error occured. Error code "
        }
        self.errorState = False

    def log(self, string):
        self.logs.append(str(string))

    def logError(self, errorMessage, var):
        self.errorState = True
        if errorMessage in self.errorMessages:
            self.log("<b style='color:red'>" + self.errorMessages[errorMessage] + "" + var + "</b>")
        else:
            self.logError("errorDuringErrorLogging", errorMessage + " does not exist!")

    def get_logs(self):
        if not self.errorState:
            self.logs.append("Done!")
        else:
            self.logs.append("Failed!")
        return "<br>".join(self.logs)
