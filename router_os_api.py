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

try:
    api = router_connection.get_api()
    try:
        list_queues = api.get_resource('/queue/simple')
        queue_id = list_queues.get(name=queueName)
        list_queues.set(id=queue_id[0]['id'], disabled="false")
        # print(json.dumps(list_queues))

    except routeros_api.exceptions.RouterOsApiCommunicationError:
        comunication_error.append(mikrotik_config['router'])

    router_connection.disconnect()
    print(mikrotik_config['router'] + '  Done')

except routeros_api.exceptions.RouterOsApiConnectionError:
    print(mikrotik_config['router'] + '  NOT done')
    no_access.append(mikrotik_config['router'])
