#!/bin/python

from faker import Faker

faker = Faker()

red_addr = set()
for i in range(0, 10):
    try:
        red_addr.add(faker.ipv4())
    except Exception:
        continue

with open('red_ips.txt', 'w+') as file:
    for ip in red_addr:
        file.write('{0}\n'.format(ip))   

