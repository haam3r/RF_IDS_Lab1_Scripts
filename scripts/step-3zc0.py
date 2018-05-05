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
    Check if new rule is in custom.rules 
    '''

    logging.debug('Starting check for step-3zc0')
    vta_step = 'step-3zc0'
    host = 'ids'
    cmds = [
        r"grep -qP '^(alert|drop)\s+((?i)icmp)\s+\$\w+\s+[[:alnum:]]+\s+(->|<>)\s+\$\w+\s+[[:alnum:]]+\s+\((?=.*?msg\:\".+\"\;)(?=.*?sid\:1\d{6}\;).*$' /etc/suricata/rules/custom.rules; echo $?"
    ]
    success = 0

    for cmd in cmds:
        ssh = subprocess.Popen(["ssh", "-o StrictHostKeyChecking=no", host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        try:
            result = ssh.stdout.readlines()[0].rstrip()
            logging.debug('Command {cmd} got result {result}'.format(cmd=cmd, result=result))
            if result.decode('UTF-8') == '0':
                success += 1
        except IndexError as err:
            logging.error('Not okay: {}'.format(err))
            sys.exit(1)

    if success == len(cmds): 
        logging.info('Marking {step} as sucessful. Correct rule in correct file.'.format(step=vta_step))
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
