import requests
import json
from configparser import ConfigParser

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
devices_url = base_url + uisp_config['unms_api_version'] + '/devices'
sites_url = base_url + uisp_config['unms_api_version'] + '/sites'

ucrm_headers = {
    'X-Auth-App-Key': uisp_config["key"], 'Content-Type': 'application/json'}
unms_headers = {
    'X-Auth-Token': uisp_config["key"], 'Content-Type': 'application/json'}

r_clients = requests.get(clients_url, headers=ucrm_headers)
r_services = requests.get(services_url, headers=ucrm_headers)
r_client_services = requests.get(client_services_url, headers=ucrm_headers)

r_clients = r_clients.json()
r_services = r_services.json()
r_client_services = r_client_services.json()
# print(r.text)

services = []

for service in r_client_services:
    # print("Service id: ", service.get('id', "No Service ID Found"))
    # print("Service status: ", service.get('status', "No service status found"))
    # print("Service client id: ", service.get(
    #    'clientId', "No service Cliend ID Found"))

    client = next(
        (item for item in r_clients if item["id"] == service['clientId']), "Client does not exist")
    # client = r_clients.get('service["clientId"]', "No Client id for service")
    # try:
    #     print(client['id'], client['firstName'], client['lastName'])
    # except:
    #     print("Client does not exist")

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
            "downloadBurstLimit": (float(service.get('downloadSpeed')) * (1 + float(mikrotik_config['burstPercentDown'])))
        })
    except:
        print("Issue with creating the services list")

for item in services:
    print(item)

# for client in r:
#     print(client['id'])
#     print(client['firstName'], client['lastName'])
#     print(client['hasSuspendedService'])
