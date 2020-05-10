from rest_framework import viewsets
from .serializers import SellerDataSerializer
from .models import SellerDetail


class SellerDetails(viewsets.ModelViewSet):
    queryset = SellerDetail.objects.all()
    serializer_class = SellerDataSerializer


