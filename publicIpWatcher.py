import os
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

class MyIpWatcher:
    def __init__(self):
        self.logFile = None
        self.publicIP = None
        self.oldIp = None

        return

    def print(self, arg):
        string = "[" + str(datetime.now()) + "][MyIpWatcher] " + arg
        if self.logFile is not None:
            self.logFile.write(string + "\n")
        print(string)

    def CheckForIpAddress(self):
        self.print("Checking for Ip Password")
        self.print("Sending request to http://whatismyip.org")

        request = Request("http://whatismyip.org", headers={'User-Agent': 'Mozilla/5.0'})
        ext_ip = urlopen(request).read()

        htmlParser = MyHTMLParser(self.logFile)
        htmlParser.feed(str(ext_ip))

        self.publicIP = htmlParser.publicIP
        self.print("Program terminated with public IP " + self.publicIP)

    def initLogFile(self):
        if not os.path.exists("log"):
            os.makedirs("log")
        self.logFile = open("log/logFile.log", "a+")

    def CheckIfUpdateIsNeeded(self):
        if os.path.exists("lastPublicIP.txt"):
            saveFile = open("lastPublicIP.txt", "r+")
            self.oldIp = saveFile.read()
            self.print("Last found IP was: " + self.oldIp)
        if self.oldIp is None or self.oldIp != self.publicIP:
            self.print("New update required - IP changed")
            self.updateNewIp()
        else:
            self.print("No public IP update is required")

    def updateNewIp(self):
        self.print("Upating Public IP...")
        newFile = open("lastPublicIP.txt", "w+")
        newFile.write(self.publicIP)

        with open("myEmailConfig.json") as json_file:
            data = json.load(json_file)
            email = data["email"]
            password = data["password"]
            destinationMail = data["destination_email"]
            subject = "[RaspBerry Pi - Public IP Watcher] - Public IP Changes"

            message = """Your Public IP has changed (at least at the current Raspberry Pi's network)\n
                Previous IP:  """ + str(self.oldIp) + """
                     New IP:  """ + str(self.publicIP) + """\nYour Raspberry PI\n"""

            msg = MIMEMultipart()
            msg["From"] = email
            msg["To"] = destinationMail
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, password)
            text = msg.as_string()
            server.sendmail(email, destinationMail, text)
            server.quit()

            self.print("E-mail sent")

        self.print("New public IP updated")

if __name__ == "__main__":
    myWatcher = MyIpWatcher()
    myWatcher.initLogFile()
    myWatcher.CheckForIpAddress()
    myWatcher.CheckIfUpdateIsNeeded()
