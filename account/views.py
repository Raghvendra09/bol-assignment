from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SellerDataSerializer
from .models import SellerDetail
import json
from rest_framework import status


class SellerData(APIView):
    def get(self, request, pk=None):
        try:
            data = SellerDetail.objects.get(id=pk)
        except SellerDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializers = SellerDataSerializer(data)
        return Response(serializers.data, status=status.HTTP_202_ACCEPTED)

    def post(self, request, pk=None):
        payload = json.loads(request.body.decode('utf-8'))
        data = SellerDetail.objects.create(client_id=payload.get('client_id'),
                                           client_secret=payload.get('client_secret'))
        serializer = SellerDataSerializer(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):  #For Update
        try:
            data = SellerDetail.objects.filter(id=pk)
            payload = json.loads(request.body.decode('utf-8'))
            data.update(**payload)
            data = SellerDetail.objects.get(id=pk)
            serializers = SellerDataSerializer(data)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except SellerDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None): #For Delete
        try:
            data = SellerDetail.objects.get(id=pk)
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SellerDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


