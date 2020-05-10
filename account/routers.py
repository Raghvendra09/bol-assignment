from rest_framework import routers
from account.viewsets import SellerDetails


router = routers.DefaultRouter()
router.register('seller', SellerDetails)
