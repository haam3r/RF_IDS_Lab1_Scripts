#!/usr/bin/python3

from faker import Faker

faker = Faker()

ips = set()
for i in range(0, 20):
    try:
        ips.add(faker.ipv4())
    except Exception:
        continue

red_addr = list(ips)[:10]
white_addr = list(ips)[11:]

with open('/root/running/red_ips.txt', 'w+') as file:
    for ip in red_addr:
        file.write('{0}\n'.format(ip))   

with open('/root/running/white_ips.txt', 'w+') as file:
    for ip in white_addr:
        file.write('{0}\n'.format(ip))   
