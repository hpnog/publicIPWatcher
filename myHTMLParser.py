from html.parser import HTMLParser
from datetime import datetime

class MyHTMLParser(HTMLParser):
    def __init__(self, logFile):
        super().__init__()
        self.foundIt = False
        self.publicIP = None
        self.logFile = logFile

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr == ("href", "/my-ip-address"):
                self.foundIt = True
                self.print("Found the reference to the public IP in html response")

    # def handle_endtag(self, tag):
    #     self.print("Encountered an end tag :", tag)

    def handle_data(self, data):
        if self.foundIt:
            self.foundIt = False
            self.publicIP = data
            self.print("Public IP is: " + data)

    def print(self, arg):
        string = "[" + str(datetime.now()) + "][MyHTMLParser] " + arg
        if self.logFile is not None:
            self.logFile.write(string + "\n")
        print(string)
