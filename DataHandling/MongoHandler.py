import pymongo
from datetime import datetime

class MongoHandler:
    def __init__(self,MONGO_CLIENT_URI):
        super().__init__()
        self.client = pymongo.MongoClient(MONGO_CLIENT_URI)
        self.products=self.client['Idealo'].Products

    def store_product(self,product):
        product['Creation dateTime']=datetime.now()
        self.products.insert_one(product)

    def if_product_exists(self,product_id):
        prod=self.products.find_one({"_id" : product_id})
        return False if prod is None else True
    
    def count_records(self):
        return self.products.count()

    def getProductsByCategory(self, category_name):
        return self.products.find({'Category':category_name})

    def getCountByCategory(self):
        return self.products.aggregate([{"$group" : {"_id":"$Category", "Record Count":{"$sum":1}}}])

    def getCategories(self):
        return self.products.distinct("Category")

    def getCategoryValueCount(self,category):
        return category+" : "+self.getProductsByCategory(category).count()
        
    def encode_key(self,key):
        return key.replace("\\", "\\\\").replace("\$", "\\u0024").replace(".", "\\u002e")

    def decode_key(self,key):
        return key.replace("\\u002e", ".").replace("\\u0024", "\$").replace("\\\\", "\\")
