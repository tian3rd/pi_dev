#!/bin/bash

# Start a new detached tmux session with title
tmux new-session -d -s ISC_Slow_Temp_EPICSdb `/opt/rtcds/anu/a1/iocmodbus/a1slowpid/start_ioc_cds_pid.sh`

