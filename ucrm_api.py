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

# gather data from UCRM
# r_clients = requests.get(clients_url, headers=ucrm_headers)
# r_services = requests.get(services_url, headers=ucrm_headers)
# r_client_services = requests.get(client_services_url, headers=ucrm_headers)

# gather data from UNMS
# r_sites = (requests.get(sites_url, headers=unms_headers)).json()
# r_devices = (requests.get(devices_url, headers=unms_headers)).json()

# format data into json
# r_clients = r_clients.json()
# r_services = r_services.json()
# r_client_services = r_client_services.json()
# r_sites = r_sites.json()
# r_devices = r_devices.json()
# print(r.text)

services = []


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
    # client = next(
    #     (item for item in r_clients if item["id"] == serviceId), None)
    return clientService


def getAllDevices():
    device = (requests.get(devices_url, headers=unms_headers)).json()
    # device = next(
    #     (item for item in r_devices if item["identification"]["site"]["id"] == siteId), None)
    return device


def getClientDevice(siteId):
    device = next(
        (item for item in allDevices if item["identification"]["site"]["id"] == siteId), None)
    return device


def getSite(siteId):
    site = (requests.get(sites_url + '/' + siteId +
                         '?ucrmDetails=true', headers=unms_headers)).json()
    return site
    # try:
    #     site = next(
    #         (item for item in r_sites if item["ucrm"]["client"]["id"] == str(clientId)), None)
    # except:
    #     return None
    # else:
    #     return site


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
            "uploadSpeed": float(service.get('uploadSpeed')),
            "downloadSpeed": float(service.get('downloadSpeed')),
            "uploadBurstLimit": (float(service.get('uploadSpeed')) * (1 + float(mikrotik_config['burstPercentUp']))),
            "downloadBurstLimit": (float(service.get('downloadSpeed')) * (1 + float(mikrotik_config['burstPercentDown']))),
            "deviceIP": device['ipAddress'].split('/', 1)[0]
        })
    except:
        print("Issue with creating the services list for site id: " +
              str(service.get('id')))

for item in services:
    print(item)
