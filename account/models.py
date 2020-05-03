from django.db import models

# Create your models here.

class SellerDetail(models.Model):
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=500)

    class Meta:
        db_table = 'seller_details'