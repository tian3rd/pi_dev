##############################################################################################################################
epicsEnvSet("IOC", "a1pemslowconfig0")
epicsEnvSet("ARCH","linux-x86_64")

# For SL7
#epicsEnvSet("TOP","${EPICS_MODULES}/modbus")
#epicsEnvSet("MDBTOP","${EPICS_MODULES}/modbus") - changed for Debian

# changed for Debian
epicsEnvSet("TOP","${EPICS_BASE}/bin/${ARCH}/modbus")
epicsEnvSet("MDBTOP","${EPICS_BASE}")

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
# Read XT1111 BIO - BIO0
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvModbusAsynConfigure("BIO0_Rd" ,"a1bio0"    ,0            ,4              ,0                  ,4           ,0        ,32	    ,"Acromag")

# Write XT1111 BIO - BIO0
#drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvModbusAsynConfigure("BIO0_Wrt" ,"a1bio0"   ,0            ,6              ,0                  ,4            ,4        ,0	    ,"Acromag")

##### ACROMAG XT1111 - BIO1
drvAsynIPPortConfigure("a1bio1","192.168.1.211:502",0,0,1)
modbusInterposeConfig("a1bio1",0,5000,0)
drvModbusAsynConfigure("BIO1_Wrt" ,"a1bio1"   ,0            ,6              ,0                  ,4            ,4        ,0	    ,"Acromag")

##### ACROMAG XT1111 - BIO2
drvAsynIPPortConfigure("a1bio2","192.168.1.212:502",0,0,1)
modbusInterposeConfig("a1bio2",0,5000,0)
drvModbusAsynConfigure("BIO2_Rd" ,"a1bio2"    ,0            ,4              ,0                  ,4           ,0        ,32	    ,"Acromag")
drvModbusAsynConfigure("BIO2_Wrt" ,"a1bio2"   ,0            ,6              ,0                  ,4            ,4        ,0	    ,"Acromag")

##### ACROMAG XT1221-000 8 Chanel Diff ADC module - ADC0
drvAsynIPPortConfigure("a1adc0","192.168.1.220:502",0,0,1)
modbusInterposeConfig("a1adc0",0,5000,0)
drvModbusAsynConfigure("ADC0_Reg","a1adc0"   ,0		,4		,0			,8	  ,4		,32	  ,"Acromag")

##### ACROMAG XT1221-000 8 Chanel Diff ADC module - ADC1
drvAsynIPPortConfigure("a1adc1","192.168.1.221:502",0,0,1)
modbusInterposeConfig("a1adc1",0,5000,0)
drvModbusAsynConfigure("ADC1_Reg","a1adc1"   ,0		,4		,0			,8		,4	,32	  ,"Acromag")

##### ACROMAG XT1221-000 8 Chanel Diff ADC module - ADC2
drvAsynIPPortConfigure("a1adc2","192.168.1.222:502",0,0,1)
modbusInterposeConfig("a1adc2",0,5000,0)
drvModbusAsynConfigure("ADC2_Reg","a1adc2"   ,0		,4		,0			,8		,4	,32	  ,"Acromag")

##### ACROMAG 966EN-RTD 6 Channel Temp
drvAsynIPPortConfigure("a1temp0","192.168.1.200:502",0,0,1)
modbusInterposeConfig("a1temp0",0,5000,0)
# register 30012 to 30017 is channel 0 in direct units of counts/resistance. register 30018-30023 is ADC counts. 
# StartAddress is -1 can access unit via ethernet address as per above.
drvModbusAsynConfigure("TEMP0_Reg","a1temp0",0		,4		,11			,6		,4	,32	  ,"Acromag")


##############################################################################################################################
dbLoadDatabase("./ACROMAG_BIO0_PEM.db")
dbLoadDatabase("./ACROMAG_BIO1_PEM.db")
dbLoadDatabase("./ACROMAG_BIO2_PEM.db")
dbLoadDatabase("./ACROMAG_ADC0_PEM.db")
dbLoadDatabase("./ACROMAG_ADC1_PEM.db")
dbLoadDatabase("./ACROMAG_ADC2_PEM.db")
dbLoadDatabase("./ACROMAG_TEMP0_PEM.db")

iocInit

