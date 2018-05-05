#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import shlex
from objectiveschecks import check

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')

def main():
    '''
    Check if Suricata is installed and at least version 4.x
    '''

    vta_step = 'step-rx10'
    host = 'ids'
    cmd = "dpkg -l | grep suricata | awk {'print $2,$3'}"
    logging.debug('Starting check {}: Suricata installed and version >= 4'.format(vta_step))
    ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        result = ssh.stdout.readlines()[0].decode('UTF-8').split(" ")
    except IndexError:
        logging.warning('Suricata not installed on host {host}'.format(host=host))
        sys.exit(1)

    logging.debug('{0} is version {1}'.format(result[0], result[1]))

    if result[0] == 'suricata' and result[1].startswith('4.'):
        logging.info('Correct version of Suricata installed on {host}'.format(host=host))
        post = check(vta_step, True)
        if post == False:
            logging.error('Setting objective {} completed has failed'.format(vta_step))
            sys.exit(1)
        else:
            logging.info('Successfully set {step} as completed'.format(step=vta_step))
    else:
        logging.info('Check failed on {}'.format(vta_step))
        sys.exit(1)


if __name__ == '__main__':
    main()
