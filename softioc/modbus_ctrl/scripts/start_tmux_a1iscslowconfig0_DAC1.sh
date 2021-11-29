#!/bin/bash

# Start a new detached tmux session with title
tmux new-session -d -s a1iscslow `/opt/rtcds/anu/a1/iocmodbus/a1iscslowconfig0/start_a1iscslowconfig0_DAC1.sh`

