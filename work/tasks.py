
from celery import Task


class SyncShipmentTask(Task):
    def run(self, seller_data, *args, **kwargs):
        print("Management Command will sync shipment.")




