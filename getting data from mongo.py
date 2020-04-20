from DataHandling.GDriveHandler import GDriveHandler
from DataHandling.MongoHandler import MongoHandler
import os
import json
from dotenv import load_dotenv
load_dotenv()


db=MongoHandler(os.getenv('MONGO_DB_API'))
count=1
for category in db.getCategories():
    products=json.loads('[]')
    for product in db.getProductsByCategory(category):
        products.append(product)
        print(count)
        count+=1
    with open('/JSON/'+str(category)+".json", "w",encoding='utf-8-sig') as outfile: 
        outfile.write(products)

