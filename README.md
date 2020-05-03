# bol-assignment

Project contains CRUD APIs `/account/<seller-id>` for seller credentials, API `/sync-shipment/<seller-id>` to sync shipments from `api.bol.com` server and API
`/list-shipments/<seller-id>` to list shipments from local server. It also provides functinality to automatically sync shipments after initial
sync is completed.

# Tech Stack 
Django (DRF), Celery, Redis, MySql database

Project has two apps, `Account` takes care of CRUD APIs for seller credentials.
<br>
POST    ->    Create
<br>
GET     ->    Retrieve 
<br>
PUT     ->  Update
<br>
DELETE  ->    Delete
<br>



`Work` app is being used for sync and list shipments based on seller id recevied from API as paramtere.


# Steps for local setup
Install MySql server
Create database with name - `bolo`
Create user with name - `bol_client`
Set password -> `bol`

Install redis server.


After setting up database, createt virtual enviorment, actiavate it and install requirements by -> `pip install -r requirements.txt`

Create db tables in db using python3 manage.py makemigrations followed by `python3 manage.py migrate`.

Start celery  and bear worker by `celery -A bol beat --loglevel=info`

Start local server by `python3 manage.py runserver`
