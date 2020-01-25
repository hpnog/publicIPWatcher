import pathlib
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from myHTMLParser import MyHTMLParser
from urllib.request import Request, urlopen

ROOT = str(pathlib.Path(__file__).parent.absolute()) + "/"

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
        if not os.path.exists(ROOT + "log"):
            os.makedirs(ROOT + "log")
        self.logFile = open(ROOT + "log/logFile.log", "a+")

    def CheckIfUpdateIsNeeded(self):
        if os.path.exists(ROOT + "lastPublicIP.txt"):
            saveFile = open(ROOT + "lastPublicIP.txt", "r+")
            self.oldIp = saveFile.read()
            self.print("Last found IP was: " + self.oldIp)
        if self.oldIp is None or self.oldIp != self.publicIP:
            self.print("New update required - IP changed")
            self.updateNewIp()
        else:
            self.print("No public IP update is required")

    def updateNewIp(self):
        self.print("Upating Public IP...")
        newFile = open(ROOT + "lastPublicIP.txt", "w+")
        newFile.write(self.publicIP)

        with open(ROOT + "myEmailConfig.json") as json_file:
            data = json.load(json_file)
            email = data["email"]
            password = data["password"]
            destinationMail = data["destination_email"]
            systemName = data["system_name"]
            subject = "[RaspBerry Pi - Public IP Watcher] - Public IP Changes"

            message = """Your Public IP has changed (at least at the current Raspberry Pi's network)\n
                Previous IP:  """ + str(self.oldIp) + """
                     New IP:  """ + str(self.publicIP) + """\nYour """ + systemName + """\n"""

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
