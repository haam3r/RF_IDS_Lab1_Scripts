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
    Check if new rule is in custom.rules 
    '''

    logging.debug('Starting check for step-3zc0')
    vta_step = 'step-3zc0'
    host = 'ids'
    cmd = 'grep -iq "alert" /etc/suricata/rules/custom.rules && grep -oqP "sid\:1\d{6}" /etc/suricata/rules/custom.rules && grep -qP "msg\:.+" /etc/suricata/rules/custom.rules; echo $?'
    ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        result = ssh.stdout.readlines()[0].split(" ")
    except IndexError:
        logging.warning('Not okay'.format(host=host))
        sys.exit(1)

    logging.debug('Exit code was {}'.format(result[0]))

    if result[0].rstrip() == '0':
        logging.info('Correct rule in correct file')
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
        logging.error('Exit code nonzero, objective not completed')
        sys.exit(1)

if __name__ == '__main__':
    main()
