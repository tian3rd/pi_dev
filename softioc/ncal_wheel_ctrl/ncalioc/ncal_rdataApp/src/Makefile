TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = ncal_rdata
# ncal_rdata.dbd will be created and installed
DBD += ncal_rdata.dbd

# ncal_rdata.dbd will be made up from these files:
ncal_rdata_DBD += base.dbd

# Include dbd files from all support applications:
ncal_rdata_DBD += drvAsynSerialPort.dbd
ncal_rdata_DBD += asyn.dbd
ncal_rdata_DBD += stream.dbd

# Add all the support libraries needed by this IOC
ncal_rdata_LIBS += asyn
ncal_rdata_LIBS += stream

# ncal_rdata_registerRecordDeviceDriver.cpp derives from ncal_rdata.dbd
ncal_rdata_SRCS += ncal_rdata_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
ncal_rdata_SRCS_DEFAULT += ncal_rdataMain.cpp
ncal_rdata_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#ncal_rdata_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
ncal_rdata_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

