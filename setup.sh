#!/bin/bash

echo "Starting LAB services" >> /root/running/setup.log
cp /root/labs/RF_IDS_Lab1_Scripts/systemd/*.service /usr/local/lib/systemd/system/
systemctl daemon-reload
cd /root/labs/RF_IDS_Lab1_Scripts/systemd
systemctl start *.service
