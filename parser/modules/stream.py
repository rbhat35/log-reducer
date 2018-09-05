class Stream(object):

    def __init__(self, filename):
        self.stream = open(filename, 'w')


    def write(self, event):
        print event
        self.stream.write(event.__str__() + "\n")
