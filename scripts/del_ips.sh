#!/bin/bash

export LC_ALL=C

# Delete red ips
while read ip; do

	echo "Delete red $ip"
	ip addr del "$ip" dev "enp0s3:$int"

done </root/running/red_ips.txt

# Delete white ips
while read ip; do

	echo "Delete white $ip"
	ip addr del "$ip" dev "enp0s3:$int"

done </root/running/white_ips.txt
