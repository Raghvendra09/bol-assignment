from django.shortcuts import render
from work.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from work.serializers import ShipmentListSerializer
from work.tasks import shipment_list_from_bol_server, sync_shipment_details
from work.utils import refresh_token
import requests
import json
from django.conf import settings

# Create your views here.


class ShipmentListView(APIView):
    def get(self, request, pk=None):
        try:
            seller_detail = SellerDetail.objects.get(id=pk)
            shipments_list = SellerShipmentDetails.objects.filter(seller=seller_detail)
            if shipments_list.count():
                shipments_list = list(shipments_list.values_list('shipment_id', flat=True))
                shipments_obj = ShipmentDetails.objects.filter(shipmentId__in=shipments_list)
                serializer = ShipmentListSerializer(shipments_obj, many=True)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                data={}
                data['error'] = 'This seller does not have any shipment.'
                return Response(data, status=status.HTTP_404_NOT_FOUND)

        except SellerDetail.DoesNotExist:
            data = {}
            data['error'] = 'Seller does not exist.'
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class SyncShipmentView(APIView):

    def check_credentials(self, seller_data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'application/json'}
        body = {'client_id': seller_data.client_id,
                'client_secret': seller_data.client_secret,
                'grant_type': 'client_credentials'
                }
        res = requests.post(url=settings.TOKEN_HOST, headers=headers, params=body)
        res = json.loads(res.text)
        if res.get('error') == 'invalid_client':
            return False
        else:
            return True

    def post(self, request, pk=None):
        try:
            seller_data = SellerDetail.objects.get(id=pk)
            if not self.check_credentials(seller_data):
                data = {}
                data['message'] ="Invalid client id and client secret, please update client id and client secret"
                return Response(data, status.HTTP_400_BAD_REQUEST)
            total_shipments = shipment_list_from_bol_server.delay(seller_data) # Added as Celery Task
            data = {}
            data['message'] = 'Sync has been initiated.'
            return Response(data, status.HTTP_202_ACCEPTED)
        except SellerDetail.DoesNotExist:
            data = {}
            data['error'] = 'Seller does not exist.'
            return Response(data, status=status.HTTP_404_NOT_FOUND)
