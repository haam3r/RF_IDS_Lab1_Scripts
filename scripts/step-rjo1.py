#!/usr/bin/python3
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
    cmds = [
        r"iptables -L FORWARD | grep -q 'NFQUEUE num 0'; echo $?",
        r"suricata --dump-config | grep -qP '^vars\.address-groups\.HOME_NET\s+=\s+\[10.10.10.0\/24\]'; echo $?",
        r"systemctl is-active --quiet suricata; echo $?",
        r"ps auxf | grep -qP '/usr/bin/[s]uricata -c /etc/suricata/suricata.yaml --pidfile /var/run/suricata.pid -q 0 -D -vvv'; echo $?",
        r"grep -iq -e 'NFQ running in standard ACCEPT/DROP mode' -e 'engine started' /var/log/suricata/suricata.log; echo $?"
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
            if result == 0:
                success += 1
        except IndexError:
            logging.warning('Suricata conf check failed with {result} for cmd {cmd}'.format(result=result, cmd=cmd))
            sys.exit(1)

    if success == len(cmds):
        logging.info('All {nr} configuration checks passed for {step}'.format(nr=len(cmds), step=vta_step))
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
        logging.error('1 or more checks failed for {step}'.format(step=vta_step))
        sys.exit(1)

if __name__ == '__main__':
    main()
