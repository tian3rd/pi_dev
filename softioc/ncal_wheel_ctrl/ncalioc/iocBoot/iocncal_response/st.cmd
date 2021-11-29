#!../../bin/linux-arm/ncal_response

## You may have to change ncal_response to something else
## everywhere it appears in this file

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/ncal_response.dbd"
ncal_response_registerRecordDeviceDriver pdbbase

## Load record instances
#dbLoadRecords("db/xxx.db","user=controls")

cd "${TOP}/iocBoot/${IOC}"

# Load Arduino support
< epics/ncal_response.cmd

iocInit

## Start any sequence programs
#seq sncxxx,"user=controls"
