import csv
class ReadCSVList:
    def __init__(self,fileName):
        super().__init__()
        if not fileName.endswith(".csv"):fileName+='.csv'
        self.setFileName(fileName)
        self.FLAG_READ_COMPLETE=False

    def setFileName(self,fileName):self.CSV_FILE_NAME=fileName

    def loadData(self,COL_POS=0,skipHeader=False):
        self.readColoumnFromFile()

    def readColoumnFromFile(self,COL_POS=0,skipHeader=False):
        if self.CSV_FILE_NAME is None: raise NotImplementedError ('CSV File name isn\'t assigned')
        self.list_of_data=[]
        try:
            with open(self.CSV_FILE_NAME,'r', newline='',encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                #If First records is header
                if skipHeader:next(reader)
                for row in reader: 
                    self.list_of_data.append(row[COL_POS].strip())
            print('Total row= '+str(len(self.list_of_data)))
        except FileNotFoundError:
            raise FileNotFoundError("[!] "+self.CSV_FILE_NAME+" Not found ! ")
        self.FLAG_READ_COMPLETE=True

    def getFileToList(self)->list:
        if not self.FLAG_READ_COMPLETE:
            raise SyntaxError('Data need to be read from file first. execute func readFile()  ')
        return self.list_of_data
