import datetime
from turtle import position
import requests
import pandas as pd
from client import FtxClient
from local_settings import ftx as settings
import schedule
import time

client = FtxClient(settings.get('api_key'), settings.get('api_secret'), settings.get('subaccount_name'))


def getMarket(pair) :
  return client.get_single_market(pair)['price']

def getCoinWallet(coin) :
  balances = client.get_balances()
  for balance in balances:
    if (balance.get('coin') == coin) :
      return balance.get('total')

def openShort(pair, currentPrice, size) :
  print("Open short at : ", currentPrice, ' with a size of : ', size, 'BTC')
  return client.place_order(market=pair, side='sell', price=currentPrice - 10, size=size, type='limit')

def closeShort(pair, currentPrice, size) :
  return client.place_order(market=pair, side='buy', price=currentPrice + 10, size=size, type='market')

def openLong(pair, currentPrice, size) :
  print("Open long at : ", currentPrice, ' with a size of : ', size, 'BTC')
  return client.place_order(market=pair, side='buy', price=currentPrice + 10, size=size, type='market')

def closeLong(pair, currentPrice, size) :
  return client.place_order(market=pair, side='sell', price=currentPrice - 10, size=size, type='market')



pair = 'BTC-PERP'
boxSize = 20

currentPosition = 'short' 
currentPrice = getMarket(pair)
usdQty = getCoinWallet('USD')
lastOrderSize = (usdQty / currentPrice) // 0.0001 * 0.0001
lastRenkoInterval = currentPrice // boxSize


print(pair)
print(currentPrice)
print(lastOrderSize)
openShort(pair, currentPrice, lastOrderSize)


def orders() :
  global currentPosition
  global lastOrderSize
  global lastRenkoInterval
  currentPrice = getMarket(pair)
  renkoInterval = currentPrice // boxSize
  print('current price : ', currentPrice)
  print('renko interval : ', renkoInterval)
  print('last renko interval : ', lastRenkoInterval)
  if (currentPosition == 'short') :
    if (renkoInterval < lastRenkoInterval) :
      lastRenkoInterval = renkoInterval
    elif (renkoInterval > lastRenkoInterval + 1) :
      closeShort(pair=pair, currentPrice=currentPrice, size=lastOrderSize)
      newSize = (getCoinWallet('USD') / currentPrice) // 0.0001 * 0.0001
      openLong(pair=pair, currentPrice=currentPrice, size=lastOrderSize)
      lastOrderSize = newSize
      currentPosition = 'long'
      lastRenkoInterval = renkoInterval
  elif (currentPosition == 'long') :
    if (renkoInterval > lastRenkoInterval) :
      lastRenkoInterval = renkoInterval
    elif (renkoInterval < lastRenkoInterval - 1) :
      closeLong(pair=pair, currentPrice=currentPrice, size=lastOrderSize)
      newSize = (getCoinWallet('USD') / currentPrice) // 0.0001 * 0.0001
      openShort(pair=pair, currentPrice=currentPrice, size=lastOrderSize)
      lastOrderSize = newSize
      currentPosition = 'short'
      lastRenkoInterval = renkoInterval



schedule.every(1).seconds.do(orders)

while 1:
  schedule.run_pending()
  time.sleep(1)
