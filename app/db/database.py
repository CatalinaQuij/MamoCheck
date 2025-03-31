from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI")
        self.client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)
        self.db = self.client[os.getenv("MONGO_DB_NAME")]

    def get_collection(self, collection_name):
        return self.db[collection_name]

database = Database()
