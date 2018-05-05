#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import shlex
import os
from objectiveschecks import check

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')

def main():
    '''
    Check if drop rule works 
    '''

    vta_step = 'step-5v02'
    host = 'ids'
    with open("/root/running/red_ips.txt") as f:
        data = f.readlines()
    src = data[-1].rstrip()

    logging.debug('Starting check for {step}'.format(step=vta_step))

    ping = subprocess.call(["ping", "-c", "1", "-I", src, "www"])
    nc = subprocess.call(["nc", "-z", "www", "80"])
    logging.debug('Ping response code was {}'.format(ping))
    logging.debug('NC code was {}'.format(nc))

    cmd = 'grep -qP "Drop.+{src}" /var/log/suricata/fast.log; echo $?'.format(src=src)
    ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        result = ssh.stdout.readlines()[0].rstrip()
        print(result)
    except IndexError:
        logging.error('Step {} failed. IndexError with grep check'.format(vta_step))
        sys.exit(1)

    if ping != 0 and result.decode('UTF-8') == '0' and nc == 0:
        logging.debug("Marking check for {step} as successful".format(step=vta_step))
        post = check(vta_step, True)
        if post == False:
            logging.error('Setting objective {} completed has failed'.format(vta_step))
            sys.exit(1)
        else:
            logging.info('Successfully set {step} as completed'.format(step=vta_step))
    else:
        logging.info('{step} check returned zero response. Drop rule not in place.'.format(step=vta_step))
        sys.exit(1)

if __name__ == '__main__':
    main()
