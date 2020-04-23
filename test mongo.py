from DataHandling.MongoHandler import MongoHandler
from dotenv import load_dotenv
import os
#Load ENVIRONMENT VARIABLES
load_dotenv()

print("start")
db=MongoHandler(os.getenv('MONGO_DB_API'))
db_secondary=MongoHandler(os.getenv('MONGO_DB_SECONDARY_API'))

print(db.isContainCategory("E-Bike"))