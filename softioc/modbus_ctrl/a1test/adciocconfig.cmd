epicsEnvSet("IOC", "adciocconfig")
epicsEnvSet("ARCH","linux-x86_64")
epicsEnvSet("TOP","${EPICS_MODULES}/modbus")
epicsEnvSet("MDBTOP","${EPICS_MODULES}/modbus")
dbLoadDatabase("$(MDBTOP)/dbd/modbus.dbd")
modbus_registerRecordDeviceDriver(pdbbase)

# Use the following commands for TCP/IP Modbus connection
# To setup a modbus connection there are three commands
# for each module.
#
# drvAsynIPPortConfigure(const char *portName,
#                        const char *hostInfo,
#                        unsigned int priority,
#                        int noAutoConnect,
#                        int noProcessEos);
drvAsynIPPortConfigure("a1adc0","192.168.1.220:502",0,0,1)

# modbusInterposeConfig(const char *portName,
#                       modbusLinkType linkType,
#                       int timeoutMsec,
#                       int writeDelayMsec)
modbusInterposeConfig("a1adc0",0,5000,0)

#drvModbusAsynConfigure(portName, (used by channel in DB file to reference this port)
#                       tcpPortName,
#                       slaveAddress,
#                       modbusFunction, (read = 4, write = 6)
#                       modbusStartAddress, (ADCs are numbered 0-7, DACs are numbered 1-8 - brilliant, huh?)
#                       modbusLength, (length in dataType units - basically the number of channels?).
#                       dataType, (16-bit signed integers = 4)
#                       pollMsec, (how frequently to request a value in [ms] - beware of making this too small with averaging on)
#                       plcType);
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvModbusAsynConfigure("ADC0_Reg","a1adc0"	  ,0			,4				,0					,8			  ,4		,32		  ,"Acromag")

dbLoadDatabase("./ACROMAG_ADC0.db")

iocInit

