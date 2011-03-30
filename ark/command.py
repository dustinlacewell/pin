from optparse import OptionParser

class ArkCommand(object):
    def __init__(self):
        self.parser = self.get_parser()

    def get_parser(self):
        return OptionParser()

    def execute(self):
        pass



    
    

