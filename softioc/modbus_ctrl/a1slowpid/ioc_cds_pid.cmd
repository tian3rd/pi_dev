# how to run:
# cd /opt/rtcds/anu/a1/iocmodbus/a1test
# ${EPICS_BASE}/bin/${EPICS_HOST_ARCH}/softIoc ioc_cds_pid.cmd 

epicsEnvSet("IOC", "ioc_cds_pid")
epicsEnvSet("ARCH","linux-x86_64")

dbLoadDatabase("./CDS_PID_ALL_LASERS_TEMP.db")

iocInit


