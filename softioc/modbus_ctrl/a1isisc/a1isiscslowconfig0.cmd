##############################################################################################################################
epicsEnvSet("IOC", "a1isislowconfig0")
epicsEnvSet("ARCH","linux-x86_64")

# For SL7
epicsEnvSet("TOP","${EPICS_MODULES}/modbus")
epicsEnvSet("MDBTOP","${EPICS_MODULES}/modbus")

# For Debian
#epicsEnvSet("TOP","${EPICS_BASE}/bin/${ARCH}/modbus")
#epicsEnvSet("MDBTOP","${EPICS_BASE}")


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
drvAsynIPPortConfigure("a1bio6","192.168.1.240:502",0,0,1)

# modbusInterposeConfig(const char *portName,
#                       modbusLinkType linkType,
#                       int timeoutMsec,
#                       int writeDelayMsec)
modbusInterposeConfig("a1bio6",0,5000,0)

#drvModbusAsynConfigure(portName, (used by channel in DB file to reference this port)
#                       tcpPortName,
#                       slaveAddress,
#                       modbusFunction, (ADC/DAC read = 4, write = 6; DIO read 1/2, write 15/5)
#                       modbusStartAddress, (ADCs are numbered 0-7, DACs are numbered 1-8 - brilliant, huh?)
#						DIO 3000(1)-ch0-3, (2)-ch4-7, (3)-ch8-11, (4)-ch12-15
#                       modbusLength, (length in dataType units - basically the number of channels?).
#                       dataType, (16-bit signed integers = 4, 16-bit unsigned = 0)
#                       pollMsec, (how frequently to request a value in [ms] - beware of making this too small with averaging on)
#                       plcType);
# Read ES2113 BIO - BIO6
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
#drvModbusAsynConfigure("BIO6_Rd" ,"a1bio6"    ,0            ,4              ,0                  ,4           ,0        ,32	    ,"Acromag")
drvModbusAsynConfigure("BIO6_Rd" ,"a1bio6"    ,0            ,3              ,53                  ,16           ,0        ,32	    ,"Acromag")

# Write ES2113 BIO - BIO6
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
#drvModbusAsynConfigure("BIO6_Wrt" ,"a1bio6"   ,0            ,6              ,0                  ,4            ,4        ,0	    ,"Acromag")
drvModbusAsynConfigure("BIO6_Wrt" ,"a1bio6"   ,0            ,6              ,59                  ,16            ,4        ,0	    ,"Acromag")

##############################################################################################################################
dbLoadDatabase("./ACROMAG_BIO6_ISI.db")

iocInit

