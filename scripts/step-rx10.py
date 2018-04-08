#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import shlex

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')

def main():
    '''
    Check if Suricata is installed and at least version 4.x
    '''

    logging.debug('Starting check: Suricata installed and version >= 4')
    vta_step = 'step-rx10'
    host = 'ids'
    cmd = "dpkg -l | grep suricata | awk {'print $2,$3'}"
    ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        result = ssh.stdout.readlines()[0].split(" ")
    except IndexError:
        logging.warning('Suricata not installed on host {host}'.format(host=host))
        sys.exit(1)

    logging.debug('Name is: {0} and version is {1}'.format(result[0], result[1]))

    if result[0] == 'suricata' and result[1].startswith('4.'):
        logging.info('Correct version of Suricata installed on {host}'.format(host=host))
        command = r"python3 /root/labs/ci-modular-target-checks/objectiveschecks.py -d {step} -y"\
                  .format(step=vta_step)
        p = subprocess.Popen(shlex.split(command),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=False)
        p.communicate()

        if p.returncode != 0:
            logging.error('Setting objective step-rx10 completed has failed')
        else:
            logging.info('Successfully set step-rx10 as completed: {}'.format(p.returncode))
    else:
        logging.info('Check failed for unknown reasons')


if __name__ == '__main__':
    main()
