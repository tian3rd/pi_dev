# how to run:
# cd /opt/rtcds/anu/a1/iocmodbus/a1test
# ${EPICS_BASE}/bin/${EPICS_HOST_ARCH}/softIoc cds_pid.cmd 

epicsEnvSet("IOC", "cds_pid")
epicsEnvSet("ARCH","linux-x86_64")

dbLoadDatabase("./CDS_PID.db")

iocInit


