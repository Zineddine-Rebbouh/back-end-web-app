import pymongo

client = pymongo.MongoClient("mongodb://zinedinerabouh:drackjosh123@cluster2-shard-00-00.04b8z.mongodb.net:27017,cluster2-shard-00-01.04b8z.mongodb.net:27017,cluster2-shard-00-02.04b8z.mongodb.net:27017/tendances_sportives_db?ssl=true&replicaSet=atlas-sruy91-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster2")
db = client["tendances_sportives_db"]

# Clear existing data (optional)
db.sports.drop()
db.entities.drop()
db.trends.drop()
db.sentiments.drop()

# Insert sample sports
db.sports.insert_many([
    {"id": "1", "name": "كرة القدم"},
    {"id": "2", "name": "كرة السلة"}
])

# Insert sample entities
db.entities.insert_many([
    {"id": "p1", "name": "محمد صلاح", "sport": "كرة القدم", "type": "player"},
    {"id": "t1", "name": "الأهلي", "sport": "كرة القدم", "type": "team"}
])

# Insert sample trends
db.trends.insert_many([
    {"sport": "كرة القدم", "timestamp": "2025-03-18T12:00:00Z", "value": 100, "entity": "p1"},
    {"sport": "كرة القدم", "timestamp": "2025-03-18T12:05:00Z", "value": 120, "entity": "t1"}
])

# Insert sample sentiments
db.sentiments.insert_many([
    {"sport": "كرة القدم", "text": "محمد صلاح يسجل هدفاً رائعاً", "sentiment": "positive", "entity": "p1"},
    {"sport": "كرة القدم", "text": "خسارة مؤسفة للأهلي", "sentiment": "negative", "entity": "t1"}
])

print("Sample data inserted!")