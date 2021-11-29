##############################################################################################################################
epicsEnvSet("IOC", "a1iscslowconfig0")
epicsEnvSet("ARCH","linux-x86_64")


#epicsEnvSet("TOP","${EPICS_BASE}/bin/${ARCH}/modbus")
#epicsEnvSet("MDBTOP","${EPICS_BASE}")

# Changes for Debian
epicsEnvSet("TOP","${EPICS_MODULES}/modbus") - changed for Debian
epicsEnvSet("MDBTOP","${EPICS_MODULES}/modbus") - changed for Debian


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

# modbusInterposeConfig(const char *portName,
#                       modbusLinkType linkType,
#                       int timeoutMsec,
#                       int writeDelayMsec)


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

##### XT1111 BIO - BIO3
drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvAsynIPPortConfigure("a1bio3","192.168.1.213:502",0,0,1)
modbusInterposeConfig("a1bio3",0,5000,0)
drvModbusAsynConfigure("BIO3_Wrt" ,"a1bio3"   ,0            ,6              ,0                  ,4            ,4        ,0	    ,"Acromag")

##### XT1111 BIO - BIO4
drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvAsynIPPortConfigure("a1bio4","192.168.1.214:502",0,0,1)
modbusInterposeConfig("a1bio4",0,5000,0)
drvModbusAsynConfigure("BIO4_Wrt" ,"a1bio4"   ,0            ,6              ,0                  ,4            ,4        ,0          ,"Acromag")

##### XT1111 BIO - BIO5
drvModbusAsynConfigure(portName ,tcpPortName ,slaveAddress ,modbusFunction ,modbusStartAddress ,modbusLength ,dataType ,pollMsec ,plcType)
drvAsynIPPortConfigure("a1bio5","192.168.1.215:502",0,0,1)
modbusInterposeConfig("a1bio5",0,5000,0)
drvModbusAsynConfigure("BIO5_Wrt" ,"a1bio5"   ,0            ,6              ,0                  ,4            ,4        ,0          ,"Acromag")

##### ACROMAG XT1221-000 8 Chanel Diff ADC module - ADC3
drvAsynIPPortConfigure("a1adc3","192.168.1.223:502",0,0,1)
modbusInterposeConfig("a1adc3",0,5000,0)
drvModbusAsynConfigure("ADC3_Reg","a1adc3"   ,0		,4		,0			,8	  ,4		,32	  ,"Acromag")

##### ACROMAG XT1221-000 8 Chanel Diff ADC module - ADC4
drvAsynIPPortConfigure("a1adc4","192.168.1.224:502",0,0,1)
modbusInterposeConfig("a1adc4",0,5000,0)
drvModbusAsynConfigure("ADC4_Reg","a1adc4"   ,0		,4		,0			,8		,4	,32	  ,"Acromag")

##### ACROMAG XT1541-000 8 Chanel Diff DAC module - DAC0
drvAsynIPPortConfigure("a1dac0","192.168.1.230:502",0,0,1)
modbusInterposeConfig("a1dac0",0,5000,0)
drvModbusAsynConfigure("DAC0_Reg","a1dac0"   ,0		,6		,1			,8		,4	,0	  ,"Acromag")
drvModbusAsynConfigure("DAC0_Rd" ,"a1dac0"    ,0            ,4              ,0                  ,1           ,0        ,32	    ,"Acromag")

##### ACROMAG XT1541-000 8 Chanel Diff DAC module - DAC1
#drvAsynIPPortConfigure("a1dac1","192.168.1.231:502",0,0,1)
#modbusInterposeConfig("a1dac1",0,5000,0)
#drvModbusAsynConfigure("DAC1_Reg","a1dac1"   ,0		,6		,1			,8		,4	,0	  ,"Acromag")

##############################################################################################################################
dbLoadDatabase("./ACROMAG_BIO3_ISC.db")
dbLoadDatabase("./ACROMAG_ADC3_ISC.db")
dbLoadDatabase("./ACROMAG_ADC4_ISC.db")
dbLoadDatabase("./ACROMAG_DAC0_ISC.db")
#dbLoadDatabase("./ACROMAG_DAC1_ISC.db")

iocInit

