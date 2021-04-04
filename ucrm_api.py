import requests
import json
from configparser import ConfigParser

config = ConfigParser()
config.read("ucrm_api.ini")
uisp_config = config['UISP']

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

for service in r_client_services:
    print("Service id: ", service['id'])
    print("Service status: ", service['status'])
    print("Service client id: ", service['clientId'])
    try:
        client = r_clients[service['clientId']]
        print(client)
    except:
        print("Client Id for service doesn't exist")

# for client in r:
#     print(client['id'])
#     print(client['firstName'], client['lastName'])
#     print(client['hasSuspendedService'])
