#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import shlex
import os
import requests
import configparser
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

import urllib3

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')

def main():
    '''
    Check if new rule fires 
    '''

    config_filename = '/root/running/lab.ini'
    logging.debug('Reading configuration from: {file}'.format(file=config_filename))
    config = configparser.ConfigParser()
    config.read(config_filename)
    
    try:
        ta_key = config.get('LAB', 'ta_key')
        virtualta_hostname = config.get('LAB', 'virtualta_hostname')
        lab_id = config.get('LAB', 'lab_id')
        uid = config.get('LAB', 'uid')

    except Exception:
        print(" Exception no Ini file or LAB section inside ini file or wrong key values")
        sys.exit(1)
    
    logging.debug('Starting check for step-m071')
    with open("/root/running/red_ips.txt") as f:
        data = f.readlines()
    src = data[-1].rstrip()
    questionanswer = list()
    questionanswer.append(src)

    response = os.system("ping -c 1 -I " + src + " www")

    logging.debug('Exit code was {}'.format(response))


    # curl -H "Content-Type: application/json" -X PUT https://portal2.rangeforce.com/api/v2/labuser_form/ -d '{"api_key":"761bc14e1a02cf43a57000c1a11eef11",  "labID":"MckZN8X24RLdAPrdQ","user":"a921a34184659f74b9f46d11fb85e635", "qname":"question-qv7", "expected":["188.8.21.21"]}'
    payload = {
        "api_key": ta_key,
        "labID": lab_id,
        "user": uid,
        "qname": "question-qv7",
        "expected": questionanswer
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
    logging.debug(payload)
    
    try:
        file = open("/root/running/step-m071.txt", 'r')
        file.close()
        logging.debug("step-m071: File found not doing anything")
    except FileNotFoundError:
        r = s.put(virtualta_hostname + '/api/v2/labuser_form/', json=payload)
        logging.debug("step-m071: Answer file not found, posted it, got answer: {r}".format(r=r))
        with open("/root/running/step-m071.txt", 'w') as m071:
            if r.status_code == requests.codes['ok']:
                m071.write(questionanswer[0])
                logging.debug("step-m071: Wrote answer {qa} to file".format(qa=questionanswer))

if __name__ == '__main__':
    main()
