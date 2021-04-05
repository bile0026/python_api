import requests
import json
from configparser import ConfigParser

from requests.api import head, request

config = ConfigParser()
config.read("ucrm_api.ini")
uisp_config = config['UISP']
mikrotik_config = config['MIKROTIK']

base_url = 'https://' + uisp_config['server_fqdn']

# urls to retrieve ucrm client information
clients_url = base_url + '/crm/api/' + \
    uisp_config['ucrm_api_version'] + '/clients'
services_url = base_url + '/crm/api/' + \
    uisp_config['ucrm_api_version'] + '/service-plans'
client_services_url = base_url + '/crm/api/' + \
    uisp_config['ucrm_api_version'] + '/clients/services/'

# urls to retrieve unms device/client information
devices_url = base_url + '/nms/api/' + \
    uisp_config['unms_api_version'] + '/devices'
sites_url = base_url + '/nms/api/' + \
    uisp_config['unms_api_version'] + '/sites'

ucrm_headers = {
    'X-Auth-App-Key': uisp_config["key"], 'Content-Type': 'application/json'}
unms_headers = {
    'X-Auth-Token': uisp_config["key"], 'Content-Type': 'application/json'}


def getClient(clientId):
    client = (requests.get(clients_url + '/' +
                           str(clientId), headers=ucrm_headers)).json()
    return client


def getClientServicePlans():
    servicePlans = (requests.get(client_services_url,
                    headers=ucrm_headers)).json()
    return servicePlans


def getClientService(serviceId):
    clientService = (requests.get(clients_url + '/services/' +
                                  str(serviceId), headers=ucrm_headers)).json()
    return clientService


def getAllDevices():
    device = (requests.get(devices_url, headers=unms_headers)).json()
    return device


def getClientDevice(siteId):
    device = next(
        (item for item in allDevices if item["identification"]["site"]["id"] == siteId), None)
    return device


def getSite(siteId):
    site = (requests.get(sites_url + '/' + siteId +
                         '?ucrmDetails=true', headers=unms_headers)).json()
    return site


# variable declarations
services = []
clientServicePlans = getClientServicePlans()
allDevices = getAllDevices()

for service in clientServicePlans:

    # find client in the client list
    clientService = getClientService(service.get('id'))

    # get the client information
    client = getClient(clientService['clientId'])

    # get site information for clients
    try:
        clientService
    except NameError:
        print("Client service not found")
    else:
        if clientService and clientService is not None and clientService['unmsClientSiteId'] is not None:
            site = getSite(clientService['unmsClientSiteId'])

    # get device information
    try:
        site
    except NameError:
        print("Site was not found for service id: " + str(service.get('id')))
    else:
        if site and site is not None:
            device = getClientDevice(site['identification']['id'])

    # build list of services and clients
    try:
        services.append({
            "serviceId": service.get('id'),
            "seriviceStatus": service.get('status'),
            "serviceClientId": service.get('clientId'),
            "clientFirstName": client['firstName'],
            "clientLastName": client['lastName'],
            "uploadSpeed": site['qos']['uploadSpeed'],
            "downloadSpeed": site['qos']['downloadSpeed'],
            "uploadBurstLimit": int((site['qos']['uploadSpeed']) * (1 + float(mikrotik_config['burstPercentUp']))),
            "downloadBurstLimit": int((site['qos']['downloadSpeed']) * (1 + float(mikrotik_config['burstPercentDown']))),
            "deviceIP": device['ipAddress'].split('/', 1)[0]
        })
    except:
        print("Issue with creating the services list for site id: " +
              str(service.get('id')))

for item in services:
    print(item)
