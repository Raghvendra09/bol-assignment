from bol.celery import app
from work.utils import refresh_token
from django.conf import settings
import requests
from django.core.cache import cache
import json
import time
import datetime
from work.serializers import SellerShipmentDetailsSerializer, ShipmentDetailsSerializer
from work.models import ShipmentFetchStatus, SellerShipmentDetails
no_of_shipments_per_page = 50


@app.task
def shipment_list_from_bol_server(seller_data):
    page_no = 1
    total_shipments = []
    while True:
        params = {"page": page_no}
        page_no += 1
        token, token_key = refresh_token(seller_data)
        headers = {"Authorization": "Bearer {}".format(token),
                   "Accept": "application/vnd.retailer.v3+json"}
        res = requests.get(url=settings.SHIPMENT_DATA_HOST, headers=headers, params=params)
        if res.status_code == 204:  #checking for no-content
            break
        if res.status_code == 401:  # Token expired
            cache.delete(token_key)
            continue
        if res.status_code == 429:   # Rate Limit Kicked in..  making it sleep till limit gets reset
            time.sleep(60)
            continue
        res = json.loads(res.text)
        shipments = res.get('shipments')
        if not shipments:
            break
        total_shipments += shipments
        if len(shipments) < no_of_shipments_per_page: # Checking if no of shipments is less then 50 in one page.. it means there is no data left
            break
    for shipment in total_shipments:
        push_shipment_list(shipment.get('shipmentId'), seller_data)
    sync_shipment_details(seller_data)
    return total_shipments


def push_shipment_list(shipment_id, seller_data):
    data = {'seller': seller_data.id,
            'shipment_id': shipment_id,
            'fetchStatusData': {
                'details_fetched': False,
                'fetched_at': datetime.datetime.now()
                                }
            }

    serializer = SellerShipmentDetailsSerializer(data=data)
    if serializer.is_valid():
        serializer.save()


def sync_shipment_details(seller_data):
    total_shipments = SellerShipmentDetails.objects.filter(seller=seller_data)
    unfetched = ShipmentFetchStatus.objects.filter(shipment__in=total_shipments).filter(details_fetched=False)
    for shipment in unfetched:
        host_url = "{}/{}".format(settings.SHIPMENT_DETAILS_HOST, shipment.shipment_id)
        while True:
            token, token_key = refresh_token(shipment.seller)
            headers = {"Authorization": "Bearer {}".format(token), "Accept": "application/vnd.retailer.v3+json"}
            res = requests.get(url=host_url, headers=headers)
            if res.status_code == 401:  # Token Expired
                cache.delete(token_key)
                continue
            if res.status_code == 200:  # Received Shipment Details
                break
            if res.status_code == 429:  # Rate Limit kicked in.. making it sleep till limit gets reset
                time.sleep(60)
                continue
        serializer = ShipmentDetailsSerializer(data=json.loads(res.text))
        if serializer.is_valid():
            serializer.save()
            shipment.details_fetched = True
            shipment.fetched_at = datetime.datetime.now()
            shipment.save()
        else:
            print(serializer.errors)
        print("")



