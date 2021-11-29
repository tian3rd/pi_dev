TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = ncal_response
# ncal_response.dbd will be created and installed
DBD += ncal_response.dbd

# ncal_response.dbd will be made up from these files:
ncal_response_DBD += base.dbd

# Include dbd files from all support applications:
ncal_response_DBD += drvAsynSerialPort.dbd
ncal_response_DBD += asyn.dbd
ncal_response_DBD += stream.dbd

# Add all the support libraries needed by this IOC
ncal_response_LIBS += asyn
ncal_response_LIBS += stream

# ncal_response_registerRecordDeviceDriver.cpp derives from ncal_response.dbd
ncal_response_SRCS += ncal_response_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
ncal_response_SRCS_DEFAULT += ncal_responseMain.cpp
ncal_response_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#ncal_response_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
ncal_response_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

