from rest_framework import serializers
from .models import SellerDetail


class SellerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerDetail
        fields = ('client_id', 'client_secret')

