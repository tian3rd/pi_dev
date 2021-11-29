epicsEnvSet("IOC", "ioclaserservo")
epicsEnvSet("ARCH","linux-x86_64")

dbLoadDatabase("./IOCLASERSERVO.db")

iocInit


