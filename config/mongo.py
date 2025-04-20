# your_app/mongo.py

from pymongo import MongoClient

client = pymongo.MongoClient("mongodb://zinedinerabouh:drackjosh123@cluster2-shard-00-00.04b8z.mongodb.net:27017,cluster2-shard-00-01.04b8z.mongodb.net:27017,cluster2-shard-00-02.04b8z.mongodb.net:27017/tendances_sportives_db?ssl=true&replicaSet=atlas-sruy91-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster2")
db = client["tendances_sportives_db"]

# Collections
entities = db["entities"]
trends = db["trends"]
sports = db["sports"]
sentiments = db["sentiments"]

