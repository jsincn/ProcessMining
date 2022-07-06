class utils:
    @staticmethod
    def load_test_file(filepath):
        f = open(filepath, "r")
        test_xml_string = f.read()
        f.close()
        return test_xml_string