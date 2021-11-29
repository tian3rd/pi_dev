#!/bin/bash

# Start a new detached tmux session with title
tmux new-session -d -s a1pemslow `/opt/rtcds/anu/a1/iocmodbus/a1pemslow0/start_a1pemslowconfig0.sh`
