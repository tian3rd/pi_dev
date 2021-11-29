#!../../bin/linux-arm/ncal_rdata

## You may have to change ncal_rdata to something else
## everywhere it appears in this file

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/ncal_rdata.dbd"
ncal_rdata_registerRecordDeviceDriver pdbbase

## Load record instances
#dbLoadRecords("db/xxx.db","user=controls")

cd "${TOP}/iocBoot/${IOC}"

# Load Arduino support
< epics/ncal_rdata.cmd

iocInit

## Start any sequence programs
#seq sncxxx,"user=controls"
