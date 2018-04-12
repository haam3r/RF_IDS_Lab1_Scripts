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
    Check if new rule fires 
    '''

    logging.debug('Starting check for step-3zc0')
    vta_step = 'step-m071'
    host = 'ids'
    with open("/root/running/red_ips.txt") as f:
        data = f.readlines()
    src = data[-1].rstrip()

    response = os.system("ping -c 1 -I " + src + " www")

    logging.debug('Exit code was {}'.format(response))

    # TODO! Set answer from src variable
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

if __name__ == '__main__':
    main()
