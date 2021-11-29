#!/bin/bash

# Start a new detached tmux session with title
tmux new-session -d -s CavityD_PID `/opt/rtcds/anu/a1/iocmodbus/a1slowpid/start_cavity_d_pid.sh`

