# how to run:
# cd /opt/rtcds/anu/n1/softioc/a1envioc
# ${EPICS_BASE}/bin/${EPICS_HOST_ARCH}/softioc ioc_env.cmd

epicsEnvSet("IOC","ioc_env")
epicsEnvSet("ARCH","linux-arm")

dbLoadDatabase("./TORPEDO_ENV_IOC.db")

iocInit
