# apps/data_collection/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..tasks import collect_youtube_data

class CollectDataView(APIView):
    def post(self, request):
        collect_youtube_data.delay()
        return Response({"message": "Data collection triggered"})