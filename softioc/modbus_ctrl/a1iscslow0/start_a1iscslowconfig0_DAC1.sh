#!/bin/bash

# Move to operating directory
cd /opt/rtcds/anu/a1/iocmodbus/a1iscslow0

# Start the modbusApp
${EPICS_BASE}/bin/${EPICS_HOST_ARCH}/modbusApp a1iscslowconfig0_DAC1.cmd
