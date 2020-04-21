from DataHandling.GDriveHandler import GDriveHandler
from DataHandling.MongoHandler import MongoHandler
import os
import json
from bson import json_util
from dotenv import load_dotenv
from util.CSVFileHandler import CSVFileOutputHandler
import unicodedata

load_dotenv()

db=MongoHandler(os.getenv('MONGO_DB_API'))

drive=GDriveHandler()
drive.authenticate(os.getenv('GDRIVE_CRENTIAL_LOCATION'))



def decode_it(data): return unicodedata.normalize('NFKD', str(data)).encode('ascii', 'ignore').decode("utf-8")
def decode_key(key): return key.replace("\\u002e", ".").replace("\\u0024", "\$").replace("\\\\", "\\")

def convert_dict_encoding(dataDict):
    temp_dict={}
    for key,value in dataDict.items():
        key=decode_key(decode_it(key))
        value=decode_it(value)
        temp_dict[key]=value
    return temp_dict

for category in db.getCategories():
    print(category)
    products=json.loads('[]')
    header=[]

    print("CSV")
    product_csv=CSVFileOutputHandler('CSV/'+category+'.csv')
    for product in db.getProductsByCategory(category):
        product=convert_dict_encoding(product)
        products.append(product)
        for key,value in product.items():
            if key not in header:
                header.append(key)
                
    #CSV
    product_csv.setFileHeader(header)
    product_csv.initializeFile(True)
    for product in products:
        product_csv.writeRow(product)
    drive.setGDriveFolderId(os.getenv('GDRIVE_FOLDER_CSV_ID'))
    drive.uploadfile('CSV/'+category+'.csv',category+'.csv')
    #JSON
    print("JSON")
    with open('JSON/'+str(category)+".json", "w",encoding='utf-8-sig') as outfile: 
        json.dump(products, outfile,default=json_util.default)
    drive.setGDriveFolderId(os.getenv('GDRIVE_FOLDER_JSON_ID'))
    drive.uploadfile('JSON/'+category+'.json',category+'.json')


