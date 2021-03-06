#!/bin/bash

export LC_ALL=C
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
\python3 /root/labs/RF_IDS_Lab1_Scripts/scripts/gen_ips.py
int=1

while read ip; do

	echo "Adding $ip"
	ip addr add "$ip" dev "enp0s3:$int"
	int=$((int+1))

done < /root/running/red_ips.txt

while read ip; do

	echo "Adding $ip"
	ip addr add "$ip" dev "enp0s3:$int"
	int=$((int+1))

done < /root/running/white_ips.txt

ip link set dev enp0s3 up
