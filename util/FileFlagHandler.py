class FileFlagHandler:
    def __init__(self,filename='FILE_FLAG'):
        super().__init__()
        if not filename.startswith('.'):filename="."+filename
        self.file_name=filename
        self.FILE_NOT_INITIATED="FILE NOT INITIATED"

    def isFileExists(self):
        try:
            open(self.file_name,'r')
            return True
        except FileNotFoundError: return False

    def setFileName(self,filename):
        self.file_name=filename

    def setDisable(self):
        open(self.file_name,'w').write("False")
        
    def setEnable(self):
        open(self.file_name,'w').write("True")
    
    def setStatus(self,data):
        open(self.file_name,'w').write(data)

    def canIrun(self) -> bool:
        if self.getStatus()=="True" :return True
        elif self.getStatus()=="False":return False

    def getStatus(self):
        return FileFlagHandler.getFlagStatus(self.file_name)

    @staticmethod
    def getFlagStatus(filename):
        try:    return open(filename,'r').read()
        except FileNotFoundError: return FileFlagHandler.FILE_NOT_INITIATED
