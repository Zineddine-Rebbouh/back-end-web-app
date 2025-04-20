# setup_mongo.py
from pymongo import MongoClient
from datetime import datetime
import datetime as dt  # For datetime.UTC

# Your MongoDB Atlas connection string
connection_string = "mongodb://zinedinerabouh:drackjosh123@cluster2-shard-00-00.04b8z.mongodb.net:27017,cluster2-shard-00-01.04b8z.mongodb.net:27017,cluster2-shard-00-02.04b8z.mongodb.net:27017/?ssl=true&replicaSet=atlas-sruy91-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster2"
client = MongoClient(connection_string)
db = client['tendances_sportives_db']

# Define migrations to match Django's expectations
migrations = [
    {"app": "admin", "name": "0001_initial", "applied": datetime.now(dt.UTC)},
    {"app": "auth", "name": "0001_initial", "applied": datetime.now(dt.UTC)},
    {"app": "contenttypes", "name": "0001_initial", "applied": datetime.now(dt.UTC)},
    {"app": "django_celery_beat", "name": "0001_initial", "applied": datetime.now(dt.UTC)},
    {"app": "sessions", "name": "0001_initial", "applied": datetime.now(dt.UTC)},
]

# Clear existing django_migrations collection to avoid duplicates (optional)
db['django_migrations'].drop()
print("Cleared existing django_migrations collection.")

# Insert migration records
db['django_migrations'].insert_many(migrations)
print("Created django_migrations collection with initial records.")