import os
import csv

class CSVFileOutputHandler:
    def __init__(self,fileName='Data.csv'):
        super().__init__()
        self.CSV_FILE_NAME=fileName
        self.init_file_flag=False
        self.CSV_FILE_HEADER=None

    def setFileName(self, fileName:str): self.CSV_FILE_NAME=fileName
    def getCSVFileName(self)->str: return self.CSV_FILE_NAME
    def isFileNameNullorEmpty(self)->bool:
        if self.CSV_FILE_NAME is None or self.CSV_FILE_NAME=='':
            return True
        return False

    def setFileHeader(self,header:list):self.CSV_FILE_HEADER=header
    def getHeader(self)->list: return self.CSV_FILE_HEADER
    
    def isHeaderinitialized(self)->bool: 
        return False if self.CSV_FILE_HEADER is None else True

    def initializeFile(self,overWriteContent=False):
        """
        Prequistes : CSV_FILE_HEADER must be defined
        Create a new file and write the header values of the file
        if file already exists and overwrite flag is True, nothing happens then
        """
        self.init_file_flag=True
        if not self.isHeaderinitialized():
            raise AssertionError("CSV_FILE_HEADER must be defined")

        if not os.path.exists(self.CSV_FILE_NAME) or overWriteContent:
            with open(self.CSV_FILE_NAME,'w',newline='',encoding='utf-8-sig') as csvfile:
                filewriter = csv.DictWriter(csvfile, fieldnames=self.CSV_FILE_HEADER)
                filewriter.writeheader()
    
    def writeRow(self,rowDict,removeExtra=False,showExtraRows=False):
        if not self.init_file_flag:raise NotImplementedError("File isn't initialized yet")
        with open(self.CSV_FILE_NAME,'a',newline='',encoding='utf-8-sig') as csvfile:
            filewriter = csv.DictWriter(csvfile, fieldnames=self.CSV_FILE_HEADER)
            if removeExtra:
                extra_header=set(rowDict.keys())-set(self.CSV_FILE_HEADER)
                if extra_header != set() and showExtraRows: print(extra_header)
                for e in extra_header:
                    del rowDict[e]
            filewriter.writerow(rowDict)