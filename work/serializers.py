from rest_framework import serializers
from work.models import ShipmentFetchStatus, SellerShipmentDetails, CustomerDetails, TransportDetails, ShipmentDetails, ShipmentItems


class ShipmentFetchStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentFetchStatus
        fields = '__all__'


class SellerShipmentDetailsSerializer(serializers.ModelSerializer):
    fetchStatusData = ShipmentFetchStatusSerializer()

    class Meta:
        model = SellerShipmentDetails
        fields = ['shipment_id', 'seller', 'fetchStatusData']

    def create(self, validated_data):
        fetch_status_data = validated_data.pop('fetchStatusData')
        seller_shipment_details = SellerShipmentDetails.objects.create(**validated_data)
        ShipmentFetchStatus.objects.create(shipment=seller_shipment_details, **fetch_status_data)
        return ShipmentFetchStatus


class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = '__all__'


class TransportDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportDetails
        fields = '__all__'


class ShipmentItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItems
        fields = ['orderItemId', 'orderId', 'latestDeliveryDate', 'orderDate', 'ean', 'title', 'offerPrice',
                  'quantity', 'offerCondition', 'fulfilmentMethod', 'shipment']


class ShipmentDetailsSerializer(serializers.ModelSerializer):
    customerDetails = CustomerDetailsSerializer()
    transport = TransportDetailsSerializer()
    shipmentItems = ShipmentItemsSerializer(many=True)

    class Meta:
        model = ShipmentDetails
        fields = ['shipmentId', 'pickUpPoint', 'shipmentDate',  'transport', 'customerDetails', 'shipmentItems',
                  'shipmentReference']

    def create(self, validated_data):
        transport_data = validated_data.pop('transport')
        transport_obj = TransportDetails.objects.create(**transport_data)
        customer_data = validated_data.pop('customerDetails')
        customer_data_obj = CustomerDetails.objects.create(**customer_data)
        shipment_items_data = validated_data.pop('shipmentItems')
        shipment_details_obj = ShipmentDetails.objects.create(transport=transport_obj,
                                                              customer_details=customer_data_obj,
                                                              **validated_data)
        for item in shipment_items_data:
            ShipmentItems.objects.create(shipment=shipment_details_obj, **item)
        return ShipmentDetails


class ShipmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentDetails
        fields = ['shipmentId', 'pickUpPoint', 'shipmentDate', 'shipmentReference', 'shipmentItems', 'transport', 'customer_details']
        depth = 1

