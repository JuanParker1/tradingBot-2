import datetime
import requests
import pandas as pd
from client import FtxClient
from local_settings import ftx as settings
import schedule
import time

client = FtxClient(settings.get('api_key'), settings.get('api_secret'), settings.get('subaccount_name'))

def getMarket() :
  print(client.get_single_market('BTC/USD')['price'])

# getMarket()

schedule.every(1).seconds.do(getMarket)

while 1:
  schedule.run_pending()
  time.sleep(1)