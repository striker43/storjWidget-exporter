import os
import os.path
from logging import exception
from mimetypes import init
from flask import Flask
import requests
import atexit
import json
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

if os.environ.get('ENV', 'prod') == 'local':
    PERSISTENCE_DIR = './'
else:
    PERSISTENCE_DIR = '/var/www/storjWidgetVolume'

if os.environ.get('LOGGING', False):
    LOGGING = True
    print("INFO: Logging enabled")
else:
    LOGGING = False
    print("INFO: Logging disabled")


nodes = os.environ.get('NODES_LIST', '').split(',')

results_cache = {}
payoutData = {}
payoutData['day'] = None


def log(message: str):
    if LOGGING:
        with open(f"{PERSISTENCE_DIR}/logs.txt", 'a') as log_file:
            log_file.write(f'{datetime.now()}: {message} \n')
            print(f'{datetime.now()}: {message}')
    else:
        print(f'{datetime.now()}: {message}')


try:
    with open(f"{PERSISTENCE_DIR}/payout_data.json", 'r') as json_file:
        payoutData = json.load(json_file)
except OSError:
    log("ERROR: Could not read " + f"{PERSISTENCE_DIR}/payout_data.json")


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

    ingress = (satellitesResponse['bandwidthDaily'][relevantDay]['ingress']['usage'] +
               satellitesResponse['bandwidthDaily'][relevantDay]['ingress']['repair'])/1000000
    egress = (satellitesResponse['bandwidthDaily'][relevantDay]['egress']['usage'] + satellitesResponse['bandwidthDaily']
              [relevantDay]['egress']['repair'] + satellitesResponse['bandwidthDaily'][relevantDay]['egress']['audit'])/1000000

    data['ingress'] += ingress
    data['egress'] += egress

    return data


def getPayoutEstimationMonth(payoutResponse, data):
    data['estimatedPayoutTotal'] += payoutResponse['currentMonth']['egressBandwidthPayout'] + \
        payoutResponse['currentMonth']['egressRepairAuditPayout'] + \
        payoutResponse['currentMonth']['diskSpacePayout']
    return data


def getPayoutEstimationToday(data):
    """Will return 0 in case not all nodes are available during day-change.

    Args:
        data (dict): Dict containing all current data.

    Returns:
        dict: Dict containing all current data with updated field 'estimatedPayoutToday'.
    """
    actualDay = str(date.today())
    if(payoutData['day'] != actualDay):
        if(data['nodesOnline'] == data['totalNodesCount']):
            payoutData[actualDay] = data['estimatedPayoutTotal']
            payoutData['day'] = actualDay
            with open(f"{PERSISTENCE_DIR}/payout_data.json", 'w') as outfile:
                json.dump(payoutData, outfile)
                log(payoutData)
                log(
                    f"INFO: Wrote new entry for {payoutData['day']}: {data['estimatedPayoutTotal']}")
        else:
            data['estimatedPayoutToday'] = 0
            return data

    data['estimatedPayoutToday'] = (
        data['estimatedPayoutTotal'] - payoutData[actualDay])
    return data


def getSpaceInfo(snoResponse, data):
    data['spaceUsed'] += snoResponse['diskSpace']['used']/1000000000000
    data['spaceAvailable'] += snoResponse['diskSpace']['available']/1000000000000
    return data


def httpRequest(ipWithPort, path):
    try:
        response = requests.get(
            'http://' + ipWithPort + '/api/' + path, timeout=5)
        return response.json()
    except requests.exceptions.Timeout as e:
        log(f'ERROR: Timeout: {e}')
        return None
    except requests.exceptions.ConnectionError as e:
        log(f'ERROR: ConnectionError: {e}')
        return None


def update_data():
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
        satellitesResponse = httpRequest(ip, 'sno/satellites')
        payoutResponse = httpRequest(ip, 'sno/estimated-payout')

        try:
            getBandwidthData(satellitesResponse, data)
            getPayoutEstimationMonth(payoutResponse, data)
            getSpaceInfo(snoResponse, data)
        except Exception as e:
            data['nodesOnline'] -= 1
            log(f'WARNING: {ip} seems to be offline or has a problem.')
            log(e)

    getPayoutEstimationToday(data)

    data['estimatedPayoutTotal'] = float(
        "{:.2f}".format(data['estimatedPayoutTotal']/100))
    data['estimatedPayoutToday'] = float(
        "{:.2f}".format(data['estimatedPayoutToday']/100))
    data['spaceUsed'] = float("{:.2f}".format(data['spaceUsed']))
    data['spaceAvailable'] = float("{:.2f}".format(data['spaceAvailable']))

    addUnits(data)

    global results_cache
    results_cache = data

    log("INFO: Updated data.")


# Query all nodes every n seconds and hold the results in memory for faster serving to the widget
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", seconds=315)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Check on startup, if persistence json file exists
if not (os.path.isfile(f"{PERSISTENCE_DIR}/payout_data.json")):
    with open(f"{PERSISTENCE_DIR}/payout_data.json", 'w') as outfile:
        json.dump(payoutData, outfile)
        log("Created empty json file because it does not exist.")

# Query data before starting the webserver
update_data()


@app.route('/bandwidth')
def get_data():
    log("INFO: Request served.")
    global results_cache
    return results_cache
