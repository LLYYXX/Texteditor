
class FileList():
    all_files_path = set()
    all_files = {}

class TextFile():
    def __init__(self, filePath,content=None,withLog=False):
        self.fileName = filePath.split("/")[-1]
        self.filePath = filePath
        self.content = content or []
        self.state = "normal"
        if withLog:
            self.content.append("# log")

class LogFile():
    def __init__(self,content=None):
        self.content = content or []


    