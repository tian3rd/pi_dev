epicsEnvSet("IOC", "myiocconfig")
epicsEnvSet("ARCH","linux-x86_64")
epicsEnvSet("TOP","${EPICS_MODULES}/modbus")
epicsEnvSet("MDBTOP","${EPICS_MODULES}/modbus")
dbLoadDatabase("$(MDBTOP)/dbd/modbus.dbd")
modbus_registerRecordDeviceDriver(pdbbase)

# Use the following commands for TCP/IP Modbus connection
# To setup a modbus connection there are three commands
# for each module.
#
# Also see http://cars9.uchicago.edu/software/epics/modbusDoc.html
#
# drvAsynIPPortConfigure(const char *portName,
#                        const char *hostInfo,
#                        unsigned int priority,
#                        int noAutoConnect,
#                        int noProcessEos);
drvAsynIPPortConfigure("a1bio1","192.168.1.210:502",0,0,1)

# modbusInterposeConfig(const char *portName,
#                       modbusLinkType linkType,
#                       int timeoutMsec,
#                       int writeDelayMsec)
modbusInterposeConfig("a1bio1",0,5000,0)

#drvModbusAsynConfigure(portName, (used by channel in DB file to reference this port)
#                       tcpPortName,
#                       slaveAddress,
#                       modbusFunction, (ADC/DAC read = 4, write = 6; DIO read 1/2, write 5)
#                       modbusStartAddress, (ADCs are numbered 0-7, DACs are numbered 1-8 - brilliant, huh?)
#                       modbusLength, (length in dataType units - basically the number of channels?).
#                       dataType, (16-bit signed integers = 4)
#                       pollMsec, (how frequently to request a value in [ms] - beware of making this too small with averaging on)
#                       plcType);
drvModbusAsynConfigure("BIO_Reg","a1bio1",0,2,0,16,0,32,"Acromag")

# DAC
#drvAsynIPPortConfigure("c3test2","10.0.1.41:502",0,0,1)
#modbusInterposeConfig("c3test2",0,5000,0)
#drvModbusAsynConfigure("DAC_Reg","c3test2",0,6,1,8,4,0,"Acromag")

# set up the binary outputs using function code "5"
#drvAsynIPPortConfigure("a1dio1","192.168.1.210:502",0,0,1)
#modbusInterposeConfig("a1dio1",0,5000,0)
#drvModbusAsynConfigure("BIO_Reg","a1dio1",0,5,0,4,0,0,"Acromag")

dbLoadDatabase("./BIOIOCTEST.db")

iocInit

