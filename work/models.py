from django.db import models
from account.models import SellerDetail
# Create your models here.



class CustomerDetails(models.Model):
    salutationCode = models.CharField(max_length=10, blank=True, null=True)
    zipCode = models.CharField(max_length=10, blank=True, null=True)
    countryCode = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'customer_details'


class TransportDetails(models.Model):
    transportId = models.BigIntegerField(primary_key=True)
    transporterCode = models.CharField(max_length=50, blank=True, null=True)
    trackAndTrace = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'transport_details'


class ShipmentDetails(models.Model):
    shipmentId = models.BigIntegerField(primary_key=True)
    pickUpPoint = models.BooleanField(blank=True, null=True)
    shipmentDate = models.DateTimeField(blank=True, null=True)
    transport = models.ForeignKey(TransportDetails, models.DO_NOTHING, blank=True, null=True)
    customer_details = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'shipment_details'


class ShipmentItems(models.Model):
    orderItemId = models.BigIntegerField(primary_key=True)
    orderId = models.BigIntegerField()
    orderDate = models.DateTimeField(blank=True, null=True)
    latestDeliveryDate = models.DateTimeField(blank=True, null=True)
    ean = models.CharField(max_length=13, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    offerPrice = models.FloatField(blank=True, null=True)
    offerCondition = models.CharField(max_length=50, blank=True, null=True)
    fulfilmentMethod = models.CharField(max_length=10, blank=True, null=True)
    shipment = models.ForeignKey(ShipmentDetails, models.DO_NOTHING, blank=True, null=True, related_name='shipmentItems')

    class Meta:
        # managed = False
        unique_together = ('orderItemId', 'orderId')
        db_table = 'shipment_items'


class SellerShipmentDetails(models.Model):
    seller = models.ForeignKey(SellerDetail, models.DO_NOTHING, blank=True, null=True)
    shipment_id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'seller_shipment_details'


class ShipmentFetchStatus(models.Model):
    shipment = models.ForeignKey(SellerShipmentDetails, models.DO_NOTHING, blank=True, null=True)
    details_fetched = models.BooleanField(blank=True, null=True)
    fetched_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shipment_fetch_status'
