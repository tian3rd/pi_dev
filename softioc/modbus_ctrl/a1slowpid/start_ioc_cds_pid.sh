#!/bin/bash

cd /opt/rtcds/anu/a1/iocmodbus/a1slowpid
${EPICS_BASE}/bin/${EPICS_HOST_ARCH}/softIoc ioc_cds_pid.cmd
