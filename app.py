from flask import Flask
import requests
import os
import time
import datetime
import json
from datetime import date
from requests.adapters import HTTPAdapter

app = Flask(__name__)

nodes = os.environ.get('NODES_LIST', '').split(',')

def getStringWithUnit(value):
  if(value < 1000):
    return str("{:.2f}".format(value)) + ' MB'
  else:
    return str("{:.2f}".format(value/1000)) + ' GB'

def addUnits(data):
  data['ingress'] = getStringWithUnit(data['ingress'])
  data['egress'] = getStringWithUnit(data['egress'])
  return data

def getRelevantDay(satellitesResponse):
  numberOfDays = len(satellitesResponse['bandwidthDaily'])
  relevantDay = None
  for i in range(0, numberOfDays):
    if(satellitesResponse['bandwidthDaily'][i]['intervalStart'].split('T')[0] == str(date.today())):
      relevantDay = i
  return relevantDay

def getBandwidthData(satellitesResponse, data):
  relevantDay = getRelevantDay(satellitesResponse)

  ingress = (satellitesResponse['bandwidthDaily'][relevantDay]['ingress']['usage'] + satellitesResponse['bandwidthDaily'][relevantDay]['ingress']['repair'])/1000000
  egress = (satellitesResponse['bandwidthDaily'][relevantDay]['egress']['usage'] + satellitesResponse['bandwidthDaily'][relevantDay]['egress']['repair'] + satellitesResponse['bandwidthDaily'][relevantDay]['egress']['audit'])/1000000

  data['ingress'] += ingress
  data['egress'] += egress

  return data
  
def getPayoutEstimationMonth(payoutResponse, data):
  data['estimatedPayoutTotal'] += payoutResponse['currentMonth']['egressBandwidthPayout'] + payoutResponse['currentMonth']['egressRepairAuditPayout'] + payoutResponse['currentMonth']['diskSpacePayout']
  return data

def getPayoutEstimationToday(snoResponse, satellitesResponse, data):
  relevantDay = getRelevantDay(satellitesResponse)

  diskAveragePayout = ((snoResponse['diskSpace']['used']/1000000000000))/720*(datetime.datetime.now().hour + (datetime.datetime.now().minute/60))*1.5
  egressPayout = (satellitesResponse['bandwidthDaily'][relevantDay]['egress']['usage']/1000000000000)*20
  repairPayout = ((satellitesResponse['bandwidthDaily'][relevantDay]['egress']['repair']/1000000000000) + (satellitesResponse['bandwidthDaily'][relevantDay]['egress']['audit']/1000000000000))*10
  
  data['estimatedPayoutToday'] += (diskAveragePayout + egressPayout + repairPayout)
  return data

def getSpaceInfo(snoResponse, data):
  data['spaceUsed'] += snoResponse['diskSpace']['used']/1000000000000
  data['spaceAvailable'] += snoResponse['diskSpace']['available']/1000000000000
  return data

def httpRequest(ipWithPort, path):
  try:
    response = requests.get('http://' + ipWithPort + '/api/' + path, timeout=5)
    return response.json()
  except requests.exceptions.Timeout:
    print("TIMEOUT ERROR")
    return None
  except requests.exceptions.ConnectionError:
    print("CONNECTION ERROR")
    return None

@app.route('/bandwidth')
def get_data():
  data = {}
  data['ingress'] = 0
  data['egress'] = 0
  data['estimatedPayoutTotal'] = 0.0
  data['estimatedPayoutToday'] = 0.0
  data['spaceUsed'] = 0.0
  data['spaceAvailable'] = 0.0
  data['totalNodesCount'] = len(nodes)
  data['nodesOnline'] = len(nodes)

  for ip in nodes:
    snoResponse = httpRequest(ip, 'sno')
    if(snoResponse != None):
      satellitesResponse = httpRequest(ip, 'sno/satellites')
      payoutResponse = httpRequest(ip, 'sno/estimated-payout')
      
      getBandwidthData(satellitesResponse, data)
      getPayoutEstimationMonth(payoutResponse, data)
      getPayoutEstimationToday(snoResponse, satellitesResponse, data)
      getSpaceInfo(snoResponse, data)
    else:
      data['nodesOnline'] -= 1
  
  data['estimatedPayoutTotal'] = float("{:.2f}".format(data['estimatedPayoutTotal']/100))
  data['estimatedPayoutToday'] = float("{:.2f}".format(data['estimatedPayoutToday']))
  data['spaceUsed'] = float("{:.2f}".format(data['spaceUsed']))
  data['spaceAvailable'] = float("{:.2f}".format(data['spaceAvailable']))

  return json.dumps(addUnits(data))