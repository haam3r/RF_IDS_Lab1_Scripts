#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import subprocess
import sys

from objectiveschecks import check

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/root/running/checks.log', filemode='a')


def main():
    '''
    Check if Suricata is configured properly and running
    '''

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

    logging.debug('Starting check {}'.format(vta_step))
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
        except IndexError:
            logging.warning('Suricata conf check failed for cmd {cmd}'.format(cmd=cmd))
            sys.exit(1)

    if success == len(cmds):
        logging.info('All {nr} configuration checks passed for {step}'.format(nr=len(cmds), step=vta_step))
        post = check(vta_step, True)
        if post is False:
            logging.error('Setting objective {} completed has failed'.format(vta_step))
            sys.exit(1)
        else:
            logging.info('Successfully set {step} as completed'.format(step=vta_step))
    else:
        logging.error('1 or more checks failed for {step}'.format(step=vta_step))
        sys.exit(1)


if __name__ == '__main__':
    main()
