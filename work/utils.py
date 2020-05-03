from django.conf import settings
import requests
import json
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache


def refresh_token(seller_data):
    token_key = "api_token_{}".format(seller_data.id)
    if not cache.get(token_key):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'application/json'}
        body = {'client_id': seller_data.client_id,
                'client_secret': seller_data.client_secret,
                'grant_type': 'client_credentials'
                }
        res = requests.post(url=settings.TOKEN_HOST, headers=headers, params=body)
        res = json.loads(res.text)
        access_token = res.get('access_token')
        expiry_time = res.get('expires_in')
        token_key = "api_token_{}".format(seller_data.id)
        cache.set(token_key, access_token, expiry_time) # Putting token in cache
        return access_token, token_key,
    else:
        return cache.get(token_key), token_key

