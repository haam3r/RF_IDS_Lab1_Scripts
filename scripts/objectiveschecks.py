#!/usr/bin/env python3

__author__ = 'Margus Ernits, Erki Naumanis'

import configparser
import requests
import sys
import json
import argparse
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')

def check(step, objective):
    '''
        Mark an objective done or failed in VTA
    '''
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    config_filename = '/root/running/lab.ini'
    logging.debug('Reading configuration from: {}'.format(config_filename))
    config = configparser.ConfigParser()
    config.read(config_filename)

    try:
        ta_key = config.get('LAB', 'ta_key')
        virtualta_hostname = config.get('LAB', 'virtualta_hostname')
        lab_id = config.get('LAB', 'lab_id')
        uid = config.get('LAB', 'uid')
    except Exception:
        logging.error(" Exception: No Ini file or LAB section inside ini file or wrong key values")
        sys.exit(1)

    # example
    # curl -H "Content-Type: application/json" -X PUT http://localhost:3013/api/v2/labuser_any/
    # -d '{"api_key":"9bbbd70dd3a0ffd35f6ee2809bfaee09", "labID":"kDMvZ2DoykiKdJavW", "userID":"MhG4PxWRsJiKNxajx",
    # "oname":"asd", "score":100, "inc":true}'
    payload = {
        "api_key": ta_key,
        "labID": lab_id,
        "user": uid,
        "oname": step,
        "done": objective
        }

    # Retry mechanism from
    #  https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    #  https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))

    # Send Obj data to VTA
    #logging.debug(payload)
    r = s.put(virtualta_hostname + '/api/v2/labuser_any', json=payload, verify=False)
    if r.status_code == requests.codes['ok']:
        return True
    else:
        return False
