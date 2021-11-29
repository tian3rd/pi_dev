#!/bin/bash

# Start a new detached tmux session with title
tmux new-session -d -s CavityA_PID `/opt/rtcds/anu/a1/iocmodbus/a1slowpid/start_cavity_a_pid.sh`

