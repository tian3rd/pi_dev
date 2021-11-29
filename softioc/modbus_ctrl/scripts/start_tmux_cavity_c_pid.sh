#!/bin/bash

# Start a new detached tmux session with title
tmux new-session -d -s CavityC_PID `/opt/rtcds/anu/a1/iocmodbus/a1slowpid/start_cavity_c_pid.sh`

