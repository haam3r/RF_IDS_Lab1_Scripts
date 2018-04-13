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

    vta_step = 'step-5v02'
    host = 'ids'
    with open("/root/running/red_ips.txt") as f:
        data = f.readlines()
    src = data[-1].rstrip()

    logging.debug('Starting check for {step}'.format(step=vta_step))

    response = os.system("ping -c 1 -I " + src + " www")
    nc = os.system("nc -z www 80")
    logging.debug('Response code was {}'.format(response))
    logging.debug('NC code was {}'.format(nc))

    cmd = 'grep -qP "Drop.+{src}" /var/log/suricata/fast.log; echo $?'.format(src=src)
    ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        result = ssh.stdout.readlines()[0].split(" ")
        logging.debug(result)
    except IndexError:
        logging.warning('Suricata not installed on host {host}'.format(host=host))
        sys.exit(1)

    if response != 0 and result[0].rstrip() == '0' and nc == 0:
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
