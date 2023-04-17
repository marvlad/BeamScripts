#!/bin/bash
# To run start in crontab like:
# crontab -e
# every minute: * * * * * /home/annie/beam_monitoring/./check_beam.sh

python3 /home/annie/beam_monitoring/BNBStatus_crontab.py
