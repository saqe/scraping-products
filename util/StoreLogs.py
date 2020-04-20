from util.ReadCSVList import ReadCSVList
class StoreCSVLogs:
    def __init__(self,fileName:str):
        super().__init__()
        if not fileName.endswith(".csv"):fileName+='.csv'
        self.setFileName(fileName)
        self.LOADED_DATA=[]

    def setFileName(self,fileName):     self.CSV_LOG_FILE_NAME=fileName
    def getFileName(self) ->str:        return CSV_LOG_FILE_NAME
    
    def loadLogs(self):
        if self.CSV_LOG_FILE_NAME==None:raise SyntaxError('File Name isn\'t defined')
        read_file=ReadCSVList(self.CSV_LOG_FILE_NAME)
        try:
            read_file.loadData()
            self.LOADED_DATA.extend(read_file.getFileToList())
            print(self.getRecordCount())
        except FileNotFoundError:
            print("[!] Logs File isn't used right now, will be created in next run.")
        

    def ifDataInLogs(self, __data__:str):   return True if str(__data__) in self.LOADED_DATA else False
    def getSetOfLogs(self)->set:        return self.LOADED_DATA

    def getRecordCount(self)->int:
        return len(self.LOADED_DATA)

    def store_data(self,__data__):
        __data__=str(__data__)
        self.LOADED_DATA.append(__data__)
        open(self.CSV_LOG_FILE_NAME,'a',newline='').write(__data__+'\n')
