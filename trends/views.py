

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pymongo

# MongoDB connection (global for simplicity; consider a separate module for production)
client = pymongo.MongoClient("mongodb://zinedinerabouh:drackjosh123@cluster2-shard-00-00.04b8z.mongodb.net:27017,cluster2-shard-00-01.04b8z.mongodb.net:27017,cluster2-shard-00-02.04b8z.mongodb.net:27017/?ssl=true&replicaSet=atlas-sruy91-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster2")
db = client["sports_trends"]

# API views


class SportsList(APIView):
    def get(self, request):
        sports = list(db.sports.find({}, {"_id": 0}))
        print("Fetched sports:", sports)
        if not sports:
            return Response({"error": "No sports found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(sports, status=status.HTTP_200_OK)

class EntitiesList(APIView):
    def get(self, request):
        id = request.query_params.get('sport')  # e.g., "2"
        if not id:
            return Response({"error": "Sport parameter required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the sport name from the sports collection
        sport_doc = db.sports.find_one({"id": id}, {"_id": 0})
        if not sport_doc:
            return Response({"error": "Invalid sport ID"}, status=status.HTTP_400_BAD_REQUEST)
        sport_name = sport_doc["name"]  # e.g., "كرة السلة"
        
        # Fetch entities
        entities = list(db.entities.find({"sport": sport_name}, {"_id": 0}))
        print("Fetched entities for sport", sport_name, ":", entities)
        if not entities:
            return Response({"message": "No entities found for this sport"}, status=status.HTTP_200_OK)
        return Response(entities, status=status.HTTP_200_OK)

class TrendsList(APIView):
    def get(self, request):
        id = request.query_params.get('sport')  # e.g., "2"
        if not id:
            return Response({"error": "Sport parameter required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the sport name from the sports collection
        sport_doc = db.sports.find_one({"id": id}, {"_id": 0})
        if not sport_doc:
            return Response({"error": "Invalid sport ID"}, status=status.HTTP_400_BAD_REQUEST)
        sport_name = sport_doc["name"]  # e.g., "كرة السلة"
        
        # Build the query
        query = {"sport": sport_name}
        entities = request.query_params.getlist('entity', [])
        if entities:
            query["entity"] = {"$in": entities}
        
        # Fetch trends
        trends = list(db.trends.find(query, {"_id": 0}))
        print("Fetched trends for sport", sport_name, ":", trends)
        if not trends:
            return Response({"message": "No trends found for this sport"}, status=status.HTTP_200_OK)
        return Response(trends, status=status.HTTP_200_OK)

class SentimentsList(APIView):
    def get(self, request):
        id = request.query_params.get('sport')  # e.g., "2"
        if not id:
            return Response({"error": "Sport parameter required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the sport name from the sports collection
        sport_doc = db.sports.find_one({"id": id}, {"_id": 0})
        if not sport_doc:
            return Response({"error": "Invalid sport ID"}, status=status.HTTP_400_BAD_REQUEST)
        sport_name = sport_doc["name"]  # e.g., "كرة السلة"
        
        # Build the query
        query = {"sport": sport_name}
        entities = request.query_params.getlist('entity', [])
        if entities:
            query["entity"] = {"$in": entities}
        
        # Fetch sentiments
        sentiments = list(db.sentiments.find(query, {"_id": 0}))
        print("Fetched sentiments for sport", sport_name, ":", sentiments)
        if not sentiments:
            return Response({"message": "No sentiments found for this sport"}, status=status.HTTP_200_OK)
        return Response(sentiments, status=status.HTTP_200_OK)