#!/usr/bin/env python3

from configparser import ConfigParser
import routeros_api
import json

config = ConfigParser()
config.read("ucrm_api.ini")
mikrotik_config = config['MIKROTIK']

no_access = []
comunication_error = []

router_connection = routeros_api.RouterOsApiPool(
    mikrotik_config['router'],
    username=mikrotik_config['username'],
    password=mikrotik_config['password'],
    port=int(mikrotik_config['port']),
    use_ssl=mikrotik_config['use_ssl'],
    ssl_verify=mikrotik_config['ssl_verify'],
    ssl_verify_hostname=mikrotik_config['ssl_verify_hostname'],
    plaintext_login=mikrotik_config['plaintext_login']
)

queueName = "CATCH_ALL_QUEUE"
services = [
    {
        "serviceId": 1,
        "serviceStatus": 1,
        "serviceClientId": 14,
        "clientFirstName": 'Bilbo',
        "clientLastName": 'Baggins',
        "maxLimitUpload": '50000000',
        "maxLimitDownload": '10000000',
        "burstLimitUpload": '50000000',
        "burstLimitDownload": '100000000',
        "burstThresholdUpload": '5000000',
        "burstThresholdDownload": '10000000',
        "queueName": 'Bilbo Baggins - Service Id: 1',
        "deviceIP": '192.168.110.1',
    },
    {
        "serviceId": 2,
        "serviceStatus": 4,
        "serviceClientId": 14,
        "clientFirstName": 'John',
        "clientLastName": 'Doe',
        "maxLimitUpload": '50000000',
        "maxLimitDownload": '10000000',
        "burstLimitUpload": '50000000',
        "burstLimitDownload": '100000000',
        "burstThresholdUpload": '5000000',
        "burstThresholdDownload": '10000000',
        "queueName": 'John Doe - Service Id: 2',
        "deviceIP": '192.168.110.1',
    },
    {
        "serviceId": 3,
        "serviceStatus": 2,
        "serviceClientId": 14,
        "clientFirstName": 'Jane',
        "clientLastName": 'Doe',
        "maxLimitUpload": '50000000',
        "maxLimitDownload": '10000000',
        "burstLimitUpload": '50000000',
        "burstLimitDownload": '100000000',
        "burstThresholdUpload": '5000000',
        "burstThresholdDownload": '10000000',
        "queueName": 'Jane Doe - Service Id: 3',
        "deviceIP": '192.168.110.1',
    },
    {
        'serviceId': 14,
        'serviceStatus': 1,
        'serviceClientId': 13,
        'clientFirstName': 'Gandalf',
        'clientLastName': 'TheGray',
        'maxLimitUpload': '5000000',
        'maxLimitDownload': '10000000',
        'burstLimitUpload': '5250000',
        'burstLimitDownload': '10500000',
        'burstThresholdUpload': '4750000',
        'burstThresholdDownload': '4750000',
        'queueName': 'Gandalf TheGray - Service Id: 14',
        'deviceIP': '192.168.100.245'
    }

]
# services.append(services)

mikrotik_config = {
    "router": '192.168.3.20',
    "burstTimeUp": '10',
    "burstTimeDown": '10',
    "catch_all_queue": 'CATCH_ALL_QUEUE'
}

# disables a given queue on a router


def disableQueue(queues, name):
    print("Disabling queue", name)
    queues.set(id=getQueueID(queues, name), disabled="true")

# enables a given queue on router


def enableQueue(queues, name):
    print("Enabling queue", name)
    queues.set(id=getQueueID(queues, name), disabled="false")

# returns a queue object


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

# returns the id of the mikrotik queue


def getQueueID(queues, name):
    found_queue_id = ""
    all_queues = queues.get()
    for item in all_queues:
        if name in item['name']:
            found_queue_id = item['id']
        else:
            continue
    if found_queue_id != "":
        return found_queue_id
    else:
        return None

# build a new queue on the router


def addQueue(queues, service):
    queues.add(
        name=service['queueName'], target=service['deviceIP'], max_limit=service['maxLimitUpload'] +
        "/"+service['maxLimitDownload'], burst_limit=service['burstLimitUpload']+"/"+service['burstLimitDownload'],
        burst_threshold=service['burstThresholdUpload'] +
        "/"+service['burstLimitDownload'],
        burst_time=mikrotik_config['burstTimeUp']+"s/"+mikrotik_config['burstTimeDown']+"s", place_before=mikrotik_config['catch_all_queue']
    )

# set all configuration for a given queue


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

# remove a queue from the router based on the queuename


def removeQueue(queues, queue_id):
    #remove_queue = getQueue(queues, queue_name)
    if queue_id:
        print("Removing ", queue_id)
        queues.remove(id=queue_id)
    else:
        print("Can't remove none queue")

# checks for queues that no longer have services and removes the queues


def cleanupQueues(queues, services):
    all_queues = queues.get()
    queue_names = list(dict([(d['id'], d['name'])
                       for d in all_queues]).values())
    queue_ids = list(dict([(d['id'], d['name'])
                           for d in all_queues]).keys())
    service_names = list(dict([(d['serviceId'], d['queueName'])
                         for d in services]).values())
    for queue in queue_names:
        if queue in service_names:
            print("Service exists, continuing...", queue)
            continue
        elif queue == mikrotik_config['catch_all_queue']:
            print("Catch all queue, continuing...", queue)
            continue
        elif queue not in service_names:
            print("Service does not exist, remove Queue", queue)
            removeQueue(queues, getQueueID(queues, queue))
        else:
            print("Service does not exist, remove Queue", queue)
            removeQueue(queues, queue)


try:
    api = router_connection.get_api()
    try:
        list_queues = api.get_resource('/queue/simple')
        # all_queues = list_queues.get()
        for service in services:
            if getQueue(list_queues, service['queueName']):
                setQueue(list_queues, service)
            else:
                addQueue(list_queues, service)

        for service in services:
            if service['serviceStatus'] == 1:
                enableQueue(list_queues, service['queueName'])
            elif service['serviceStatus'] == 3:
                disableQueue(list_queues, service['queueName'])
                print("Service Suspended - Disabling service for Service ID: ",
                      service['serviceClientId'])
            else:
                disableQueue(list_queues, service['queueName'])
                print("Not active - Disabling service for Service ID: ",
                      service['serviceClientId'])

        # cleanup queues and remove queues that no longer have a service attached
        cleanupQueues(list_queues, services)

    except routeros_api.exceptions.RouterOsApiCommunicationError:
        comunication_error.append(mikrotik_config['router'])

    router_connection.disconnect()
    print(mikrotik_config['router'] + '  Done')

except routeros_api.exceptions.RouterOsApiConnectionError:
    print(mikrotik_config['router'] + '  NOT done')
    no_access.append(mikrotik_config['router'])
