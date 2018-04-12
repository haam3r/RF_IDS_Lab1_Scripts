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
    cmds = [
        'grep -iPq "[alert|drop]" /etc/suricata/rules/custom.rules; echo $?',
        'grep -oqP "sid\:1\d{6}" /etc/suricata/rules/custom.rules; echo $?',
        'grep -qP "msg\:.+" /etc/suricata/rules/custom.rules; echo $?'
    ]
    success = 0

    for cmd in cmds:
        ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        try:
            result = ssh.stdout.readlines()[0].split(" ")
            logging.debug('Command {cmd} got result {result}'.format(cmd=cmd, result=result))
            if result[0].rstrip() == '0':
                success += 1
        except IndexError:
            logging.warning('Not okay'.format(host=host))
            sys.exit(1)

    logging.debug('Exit code was {}'.format(result[0]))

    if success == len(cmds): 
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
