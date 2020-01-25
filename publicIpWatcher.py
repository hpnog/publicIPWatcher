from myIpWatcher import MyIpWatcher

if __name__ == "__main__":
    myWatcher = MyIpWatcher()
    myWatcher.initLogFile()
    myWatcher.CheckForIpAddress()
    myWatcher.CheckIfUpdateIsNeeded()
