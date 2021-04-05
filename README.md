# python_api
various python scripts using the requests module

# UCRM_API
Create an .ini file in the same directory as the `ucrm_api.py` script with this format.
```
[UCRM]
server_fqdn = <your_ucrm_server_fqdn>
key = <your_ucrm_api_key>
api_version = v1.0

[MIKROTIK]
router = <router_ip_or_fqdn>
port = 8728
username = <username>
password = <password>
# burst max in decimal format
burstPercentUp = .05
# burst max in decimal format
burstPercentDown = .05
# burst time in seconds
burstTimeUp = 10
# bust time in seconds
burstTimeDown = 10
# alow burst at percentage in decimal
limitAtUp = .95
# alow burst at percentage in decimal
limitAtDown = 95
```
