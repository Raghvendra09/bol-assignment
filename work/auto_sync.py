from celery import Celery
from work.models import  SellerDetail, ShipmentFetchStatus
import datetime
from work.utils import check_credentials
from work.tasks import SyncShipmentTask
from django.conf import settings
from celery import Task
app = Celery()


class AutoSyncTask(Task):
    def run(self, source, *args, **kwargs):
        last_hour = datetime.datetime.now() - datetime.timedelta(hours=settings.AUTO_SYNC_FREQUENCY_INTERVAL)
        seller_with_latest_sync = ShipmentFetchStatus.objects.filter(fetched_at__gte=last_hour).values(
            'shipment__seller').distinct()
        for seller in seller_with_latest_sync:
            seller_data = SellerDetail.objects.get(id=seller.get('shipment__seller'))
            if not check_credentials(seller_data):  # After initial sync.. credentials has been updated
                pass
            task = SyncShipmentTask()
            task.run(seller_data)
        return


