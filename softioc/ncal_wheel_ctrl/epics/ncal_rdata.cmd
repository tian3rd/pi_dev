# BEGIN ncal_response.cmd ------------------------------------------------------------

# http://www.aps.anl.gov/epics/modules/soft/asyn/R4-18/asynDriver.html


############ documentation for the IOC commands #################################
#epicsEnvSet("NCAL_RESPONSE","/home/controls/Documents/gravforcecal/arduino/ncal_response/epics")
#cd ${CMD_RESPONSE}

# Set up 1 local serial port(s)

# USB 0 connected to Arduino at 115200 baud
#drvAsynSerialPortConfigure("portName","ttyName",priority,noAutoConnect, noProcessEos)
#asynOctetSetInputEos(const char *portName, int addr, const char *eosin,const char *drvInfo)
#asynOctetSetOutputEos(const char *portName, int addr, const char *eosin,const char *drvInfo)

# Make port available from the iocsh command line
#asynOctetConnect(const char *entry, const char *port, int addr, int timeout_ms, int buffer_len, const char *drvInfo)

# define the serial port and connect it with asyn
#dbLoadRecords("$(ASYN)/db/asynRecord.db","P=$(IOC_PREFIX)cr:,PORT=usb0,R=asyn_1,ADDR=0,OMAX=256,IMAX=256")

# define specific Arduino I/O to be used
#dbLoadRecords("ncal_response.db","P=$(IOC_PREFIX)cr:,PORT=usb0")
############################################################################

epicsEnvSet("NCAL_EPICS","/home/controls/Documents/ncal_wheel_ctrl/epics")
epicsEnvSet("ASYN","/home/controls/projects/epics/modules/asyn")

drvAsynSerialPortConfigure("serial0", "/dev/ttyAMA0", 0, 0, 0)
asynSetOption("serial0", 0, baud, 115200)
asynOctetSetInputEos("serial0", 0, "\r\n")
asynOctetSetOutputEos("serial0", 0, "\n")

asynOctetConnect("serial", "serial0", 0, 10)

# ask device to report device ID string
# asynOctetWriteRead("serial0","?id\n")

# ask device to report device software version
#asynOctetWriteRead("serial0","?v\n")

dbLoadRecords("${ASYN}/db/asynRecord.db","P=N1:NCAL-,PORT=serial0,R=asyn_1,ADDR=0,OMAX=256,IMAX=256")
dbLoadRecords("${NCAL_EPICS}/ncal_rdata.db","P=N1:NCAL-,PORT=serial0")

# turn on diagnostics:
#   asynSetTraceIOMask "usb0" 0 2
#   asynSetTraceMask   "usb0" 0 9

# END ncal_response.cmd --------------------------------------------------------------

