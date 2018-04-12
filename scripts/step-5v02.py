#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import shlex
import os

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')

def main():
    '''
    Check if drop rule works 
    '''

    logging.debug('Starting check for step-3zc0')
    vta_step = 'step-5v02'
    host = 'ids'
    with open("/root/running/red_ips.txt") as f:
        data = f.readlines()
    src = data[-1].rstrip()

    response = os.system("ping -c 1 -I " + src + " www")

    logging.debug('Response code was {}'.format(response))

    if response != 0:
        logging.debug("Marking check for {step} as successful".format(step=vta_step))
        command = r"python3 /root/labs/ci-modular-target-checks/objectiveschecks.py -d {step} -y"\
                    .format(step=vta_step)
        p = subprocess.Popen(shlex.split(command),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=False)
        p.communicate()
    
        if p.returncode != 0:
            logging.error('Setting objective {step} completed has failed'.format(step=vta_step))
            sys.exit(1)
        else:
            logging.info('Successfully set {step} as completed: {ret}'.format(step=vta_step, ret=p.returncode))
    else:
        logging.info('{step} check returned zero response. Drop rule not in place.'.format(step=vta_step))

if __name__ == '__main__':
    main()