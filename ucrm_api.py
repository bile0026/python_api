import requests
import json
from configparser import ConfigParser
from requests.api import head, request
import routeros_api

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


def disableQueue(queues, name):
    all_queues = queues.get()
    for item in all_queues:
        if name in item['name']:
            queues.set(id=item['id'], disabled="true")


def enableQueue(queues, name):
    all_queues = queues.get()
    for item in all_queues:
        if name in item['name']:
            queues.set(id=item['id'], disabled="false")


def getQueue(queues, name):
    found_queue = {}
    all_queues = queues.get()
    for item in all_queues:
        if name in item['name']:
            found_queue = item
        else:
            continue
    if found_queue:
        return found_queue
    else:
        return None


def addQueue(queues, service):
    queues.add(
        name=service['queueName'], target=service['deviceIP'], max_limit=service['maxLimitUpload'] +
        "/"+service['maxLimitDownload'], burst_limit=service['burstLimitUpload']+"/"+service['burstLimitDownload'],
        burst_threshold=service['burstThresholdUpload'] +
        "/"+service['burstLimitDownload'],
        burst_time=mikrotik_config['burstTimeUp']+"s/"+mikrotik_config['burstTimeDown']+"s", place_before=mikrotik_config['catch_all_queue']
    )


def setQueue(queues, service):
    # queues = queues.get()
    set_queue = getQueue(queues, service['queueName'])
    queues.set(
        id=set_queue['id'], name=service['queueName'], target=service['deviceIP'], max_limit=service['maxLimitUpload'] +
        "/"+service['maxLimitDownload'], burst_limit=service['burstLimitUpload']+"/"+service['burstLimitDownload'],
        burst_threshold=service['burstThresholdUpload'] +
        "/"+service['burstLimitDownload'],
        burst_time=mikrotik_config['burstTimeUp'] +
        "s/"+mikrotik_config['burstTimeDown']+"s"
    )


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
            "maxLimitUpload": str(site['qos']['uploadSpeed']),
            "maxLimitDownload": str(site['qos']['downloadSpeed']),
            "burstLimitUpload": str(int((site['qos']['uploadSpeed']) * (1 + float(mikrotik_config['burstLimitUpload'])))),
            "burstLimitDownload": str(int((site['qos']['downloadSpeed']) * (1 + float(mikrotik_config['burstLimitDownload'])))),
            "burstThresholdUpload": str(int((site['qos']['uploadSpeed']) * float(mikrotik_config['burstThresholdUpload']))),
            "burstThresholdDownload": str(int((site['qos']['uploadSpeed']) * float(mikrotik_config['burstThresholdDownload']))),
            "queueName": (client['firstName'] + " " + client['lastName'] + " - " + "Service Id: " + str(service.get('id'))),
            "deviceIP": device['ipAddress'].split('/', 1)[0],
        })
    except:
        print("Issue with creating the services list for site id: " +
              str(service.get('id')))

# for item in services:
#     print(item)

# router_connection = routeros_api.RouterOsApiPool(
#     str(mikrotik_config['router']),
#     username=str(mikrotik_config['username']),
#     password=str(mikrotik_config['password']),
#     port=int(mikrotik_config['port']),
#     use_ssl=str(mikrotik_config['use_ssl']),
#     ssl_verify=str(mikrotik_config['ssl_verify']),
#     ssl_verify_hostname=str(mikrotik_config['ssl_verify_hostname']),
#     plaintext_login=str(mikrotik_config['plaintext_login'])
# )

router_connection = routeros_api.RouterOsApiPool(
    '192.168.3.20',
    username='api',
    password='api',
    port=8728,
    plaintext_login=True
)

# connect to the router and attempt to create the queues
try:
    api = router_connection.get_api()
    try:
        list_queues = api.get_resource('/queue/simple')
        all_queues = list_queues.get()
        for service in services:
            for queue in all_queues:
                if service['status'] == 1 and

            list_queues.add(
                name=service['queueName'], target=service['deviceIP'], max_limit=service['maxLimitUpload'] +
                "/"+service['maxLimitDownload'], burst_limit=service['burstLimitUpload']+"/"+service['burstLimitDownload'],
                burst_threshold=service['burstThresholdUpload'] +
                "/"+service['burstLimitDownload'],
                burst_time=mikrotik_config['burstTimeUp']+"s/"+mikrotik_config['burstTimeDown']+"s", place_before=mikrotik_config['catch_all_queue'])
    except routeros_api.exceptions.RouterOsApiCommunicationError:
        print(mikrotik_config['router'] + '  comms error')

    router_connection.disconnect()

except routeros_api.exceptions.RouterOsApiConnectionError:
    print(mikrotik_config['router'] + '  NOT done')
