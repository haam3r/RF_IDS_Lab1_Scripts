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
    Check if Suricata is configured properly and running 
    '''

    logging.debug('Starting check step-rjo1')
    vta_step = 'step-rjo1'
    host = 'ids'
    cmd = 'grep -i "engine started" /var/log/suricata/suricata.log >> /dev/null && grep -i "AFP capture threads are running" /var/log/suricata/suricata.log >> /dev/null; echo $?'
    ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        result = ssh.stdout.readlines()[0].split(" ")
    except IndexError:
        logging.warning('Suricata not installed on host {host}'.format(host=host))
        sys.exit(1)

    logging.debug('Exit code is {}'.format(result[0]))

    if result[0].rstrip() == '0':
        logging.info('Correct version of Suricata installed on {host}'.format(host=host))
        command = r"python3 /root/labs/ci-modular-target-checks/objectiveschecks.py -d {step} -y"\
                  .format(step=vta_step)
        p = subprocess.Popen(shlex.split(command),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=False)
        p.communicate()
    
        if p.returncode != 0:
            logging.error('Setting objective {step} completed has failed'.format(step=vta_step))
        else:
            logging.info('Successfully set {step} as completed: {ret}'.format(step=vta_step, ret=p.returncode))
    else:
        print('Exit code nonzero, objective not completed')

if __name__ == '__main__':
    main()
