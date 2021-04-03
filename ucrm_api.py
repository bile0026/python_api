import requests
import json
from configparser import ConfigParser

config = ConfigParser()
config.read("ucrm_api.ini")
ucrm_config = config['UCRM']


clients_url = 'https://' + ucrm_config['server_fqdn'] + '/crm/api/v1.0/clients'
services_url = 'https://' + \
    ucrm_config['server_fqdn'] + '/crm/api/v1.0/service-plans'
client_services_url = 'https://' + \
    ucrm_config['server_fqdn'] + '/crm/api/v1.0/clients/services/'

headers = {
    'X-Auth-App-Key': ucrm_config["key"], 'Content-Type': 'application/json'}

r_clients = requests.get(clients_url, headers=headers)
r_services = requests.get(services_url, headers=headers)
r_client_services = requests.get(client_services_url, headers=headers)

r_clients = r_clients.json()
r_services = r_services.json()
r_client_services = r_client_services.json()
# print(r.text)

for service in r_client_services:
    print(service['status'])
    print(service['clientId'])
    try:
      print(r_clients[(service['clientId'])])
    except:
      print("Client Id for service doesn't exist: ", r_clients['clientId']

# for client in r:
#     print(client['id'])
#     print(client['firstName'], client['lastName'])
#     print(client['hasSuspendedService'])
