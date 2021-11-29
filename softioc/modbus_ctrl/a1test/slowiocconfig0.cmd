##############################################################################################################################
epicsEnvSet("IOC", "slowiocconfig0")
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
drvAsynIPPortConfigure("a1bio0","192.168.1.210:502",0,0,1)

# modbusInterposeConfig(const char *portName,
#                       modbusLinkType linkType,
#                       int timeoutMsec,
#                       int writeDelayMsec)
modbusInterposeConfig("a1bio0",0,5000,0)

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
# Read XT1111 BIO
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvModbusAsynConfigure("BIO0_Rd" ,"a1bio0"    ,0            ,4              ,0                  ,4           ,0        ,32	    ,"Acromag")

# Write XT1111 BIO
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvModbusAsynConfigure("BIO0_Wrt" ,"a1bio0"   ,0            ,6              ,0                  ,4            ,4        ,0	    ,"Acromag")
#drvModbusAsynConfigure("BIO0_Wrt1" ,"a1bio0"   ,0            ,6              ,1                  ,4            ,4        ,0	    ,"Acromag")

##### ACROMAG XT1221-000 8 Chanel Diff ADC module
drvAsynIPPortConfigure("a1adc0","192.168.1.220:502",0,0,1)
modbusInterposeConfig("a1adc0",0,5000,0)
drvModbusAsynConfigure("ADC0_Reg","a1adc0"	,0		,4		,0		,8		,4	,32	  ,"Acromag")

##### ACROMAG 966EN-RTD 6 Channel Temp
drvAsynIPPortConfigure("a1temp0","192.168.1.200:502",0,0,1)
modbusInterposeConfig("a1temp0",0,5000,0)
drvModbusAsynConfigure("TEMP0_Reg","a1temp0",0,4,10,6,4,32,"Acromag") # register 40011 is channel 0 in direct units of resistance


##############################################################################################################################
dbLoadDatabase("./ACROMAG_BIO0.db")
dbLoadDatabase("./ACROMAG_ADC0.db")
dbLoadDatabase("./ACROMAG_TEMP0.db")

iocInit


