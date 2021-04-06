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
    '192.168.3.20',
    username='api',
    password='api',
    port=8728,
    plaintext_login=True
)

queueName = "CATCH_ALL_QUEUE"

service = {
    "serviceId": 2,
    "seriviceStatus": 1,
    "serviceClientId": 14,
    "clientFirstName": 'Zach',
    "clientLastName": 'Biles',
    "maxLimitUpload": '50000000',
    "maxLimitDownload": '10000000',
    "burstLimitUpload": '50000000',
    "burstLimitDownload": '100000000',
    "burstThresholdUpload": '5000000',
    "burstThresholdDownload": '10000000',
    "queueName": 'Zach Biles - Service Id: 2',
    "deviceIP": '192.168.110.1',
}

mikrotik_config = {
    "router": '192.168.3.20',
    "burstTimeUp": '10',
    "burstTimeDown": '10',
    "catch_all_queue": 'CATCH_ALL_QUEUE'
}


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


def removeQueue(queues, service):
    remove_queue = getQueue(queues, service['queueName'])
    queues.remove(id=remove_queue['id'])


try:
    api = router_connection.get_api()
    try:
        list_queues = api.get_resource('/queue/simple')
        # all_queues = list_queues.get()
        if getQueue(list_queues, service['queueName']):
            setQueue(list_queues, service)
        else:
            addQueue(list_queues, service)

    except routeros_api.exceptions.RouterOsApiCommunicationError:
        comunication_error.append(mikrotik_config['router'])

    router_connection.disconnect()
    print(mikrotik_config['router'] + '  Done')

except routeros_api.exceptions.RouterOsApiConnectionError:
    print(mikrotik_config['router'] + '  NOT done')
    no_access.append(mikrotik_config['router'])
