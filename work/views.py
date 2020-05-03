from work.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from work.serializers import ShipmentListSerializer
from work.tasks import SyncShipmentTask
from work.utils import check_credentials

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
    def post(self, request, pk=None):
        try:
            seller_data = SellerDetail.objects.get(id=pk)
            if not check_credentials(seller_data):
                data = {}
                data['message'] ="Invalid client id and client secret, please update client id and client secret"
                return Response(data, status.HTTP_400_BAD_REQUEST)
            sync_task = SyncShipmentTask()
            total_shipments = sync_task.delay(seller_data) # Added as Celery Task
            data = {}
            data['message'] = 'Sync has been initiated.'
            return Response(data, status.HTTP_202_ACCEPTED)
        except SellerDetail.DoesNotExist:
            data = {}
            data['error'] = 'Seller does not exist.'
            return Response(data, status=status.HTTP_404_NOT_FOUND)
