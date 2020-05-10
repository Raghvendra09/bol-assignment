from django.core.management.base import BaseCommand, CommandError
import asyncio
import datetime
from work.models import  SellerDetail, SellerShipmentDetails, ShipmentFetchStatus
from work.serializers import SellerShipmentDetailsSerializer, ShipmentDetailsSerializer
import json
import requests
from django.core.cache import cache
from django.conf import settings
from work.utils import refresh_token
import aiohttp
import time


class Command(BaseCommand):
    help = 'Command to do........'

    def add_argument(self, parser):
        pass

    async def fetch(self, client, url, params, headers):
        async with client.post(url, headers=headers, params=params) as resp:
            return await resp

    async def sync_shipment(self, seller_data):
        seller_data = SellerDetail.objects.get(id=seller_data)
        total_shipments = []
        fulfilment_method = ['FBB', 'FBR']
        async with aiohttp.ClientSession() as client:
            for method in fulfilment_method:
                page_no = 1
                while True:
                    params = {"page": page_no}
                    page_no += 1
                    token, token_key = refresh_token(seller_data)
                    headers = {"Authorization": "Bearer {}".format(token),
                               "Accept": "application/vnd.retailer.v3+json"}
                    host = "{}?fulfilment-method={}".format(settings.SHIPMENT_DETAILS_HOST, method)
                    res = await self.fetch(client, host, params, headers)
                    # res = requests.get(url=host, headers=headers, params=params)
                    if res.status_code == 204:  # checking for no-content
                        break
                    if res.status_code == 401:  # Token expired
                        cache.delete(token_key)
                        continue
                    if res.status_code == 429:  # Rate Limit Kicked in..  making it sleep till limit gets reset
                        await asyncio.sleep(settings.RATE_LIMIT_RESET_TIME)
                        continue
                    res = json.loads(res.text)
                    shipments = res.get('shipments')

                    if not shipments:
                        break
                    total_shipments += shipments
                    if len(shipments) < settings.SHIPMENT_COUNT_PER_PAGE:  # Checking if no of shipments is less then 50 in one page.. it means there is no data left
                        break
            for shipment in total_shipments:
                self.push_shipment_list(shipment.get('shipmentId'), seller_data)
            await self.sync_shipment_details(seller_data, client)
            return

    def push_shipment_list(self, shipment_id, seller_data):
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

    async def sync_shipment_details(self, seller_data, client):
        total_shipments = SellerShipmentDetails.objects.filter(seller=seller_data)
        unfetched = ShipmentFetchStatus.objects.filter(shipment__in=total_shipments).filter(details_fetched=False)
        if unfetched.count():

            for shipment in unfetched:
                host_url = "{}/{}".format(settings.SHIPMENT_DETAILS_HOST, shipment.shipment_id)
                while True:
                    token, token_key = refresh_token(seller_data)
                    headers = {"Authorization": "Bearer {}".format(token),
                               "Accept": "application/vnd.retailer.v3+json"}
                    res = await self.fetch(client, host_url, None, headers)
                    if res.status_code == 401:  # Token Expired
                        cache.delete(token_key)
                        continue
                    if res.status_code == 200:  # Received Shipment Details
                        break
                    if res.status_code == 429:  # Rate Limit kicked in.. making it sleep till limit gets reset
                        await asyncio.sleep(settings.RATE_LIMIT_RESET_TIME)
                        continue
                serializer = ShipmentDetailsSerializer(data=json.loads(res.text))
                if serializer.is_valid():
                    serializer.save()
                    shipment.details_fetched = True
                    shipment.fetched_at = datetime.datetime.now()
                    shipment.save()
                else:
                    print(serializer.errors)
        else:
            print("Nothing to fetch ")

    async def main(self, seller_id_list):
        for seller_id in seller_id_list:
            asyncio.create_task(self.sync_shipment(seller_id))


    def handle(self, *args, **options):
        task_list = cache.get('celery_task_list')
        asyncio.run(self.main(task_list))
        cache.set('celery_task_list', [], None) # completed syncing of all shipments







