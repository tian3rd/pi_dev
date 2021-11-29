RPI setup to run the Lab environmental monitoring

It reads the sensors connected to the the RPI, and get the data from the Purple Air particle counter.

![](TORPEDO_ENV.jpg)

# Installation

All of the softioc services are to be installed in

`/opt/rtcds/anu/n1/softioc/`

and then clone the service from the git.

Once you have cloned the service, see to go into the new directory, here `torpedo_env_ctrl`, e.g

`/opt/rtcds/anu/n1/softioc/torpedo_env_ctrl`

There will be up to 4 directories, which are used as follows:

- **ini** - 
This hold the standalone_edc edc.ini file including the header details. If there is already a standalone_edc service running then you only have to manually copy the channel names into the excisting edc.ini file.

- **ioc** - 
This hold the files for the EPICS softIoc service, and used incase when there is no pcaspy implementation. This service is the fully fletched EPICS IOC server, with all its capabilities. To interact one can use the pyepics modules, or the EPICS interface. These files are obsolete but maintained for reference.

- **python** - 
This hold the python implementations of the service. This can be based on the EPICS softIoc server or the python based pcaspy implementation. I tried to make that clear by adding `_ioc` for the EPICS softIoc server, or `_ss` for the pcaspy SimpleServer implementation. The remained of this installation instruction is based on the pcaspy SimpleServer implementation (ala `_ss`). 

- **systemd** - 
This hold the files for installation of the python script to run and managed by the OS systemd service. This will help keep the python implementation operational.

Once the code is cloned we can copy the various file into their appropriate locations

Copy the systemd service into position

`$ sudo cp systemd/torpedo_env_ctrl_service.service /etc/systemd/system/`

`$ sudo chmod 664 /etc/systemd/system/torpedo_env_ctrl_service.service`

`$ sudo mkdir /usr/local/lib/torpedo_env_ctrl_service`

`$ sudo cp python/torpedo_env_ctrl_ss.py /usr/local/lib/torpedo_env_ctrl_service/torpedo_env_ctrl.py`

or, but only if we want to revert back to the orginal implementation. Currently not adviced.

`$ sudo cp python/Main_Envirodata_ProcessStart_V1.py /usr/local/lib/torpedo_env_ctrl_service/torpedo_env_ctrl.py`

# Enableing and starting the service

`$ sudo systemctl daemon-reload`

enable with

`$ sudo systemctl enable torpedo_env_ctrl_service.service`

start with

`$ sudo systemctl start torpedo_env_ctrl_service.service`

check status with 

`$ sudo systemctl status torpedo_env_ctrl_service.service`

# Recording the EPICS channels

The EPICS channels need to be obtained by the `standalone_edc` service on one of the front-end machines. In our case this is on the N1FE1 machine.

In the **ini** directory there is a file `torpedo_env_ctrl_ini_content.txt`. the content of the feil needs to be copied into the `edc.ini` file for the `standalone_edc` service.

```
# Auto generated file by torpedo_env_ctrl_ss.py
# at 2021-09-14 13:07:07
#
# Using the default parameters
[default]
gain=1.00
acquire=3
dcuid=52
ifoid=0
datatype=4
datarate=16
offset=0
slope=1.0
units=undef
#
#
# Following content lines to be manually added to the
# edc.ini file, which points to /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini
# Then the standalone_edc service (rts-edc.service on n1fe1) and the daqd
# service (rts-daqd.service on the n1fb10) will need to be restarted to
# the changes into effect.
#
[N1:PEM-LAB_PT1000_TEMP_C]
[N1:PEM-LAB_HUMIDITY]
[N1:PEM-LAB_PRESSURE_MBAR]
[N1:PEM-LAB_HTU210F_TEMP_C]
[N1:PEM-LAB_PURPLEAIR_TEMP_C]
[N1:PEM-LAB_PURPLEAIR_HUMIDITY]
[N1:PEM-LAB_PURPLEAIR_DEWPOINT_C]
[N1:PEM-LAB_PURPLEAIR_PRESSURE_MBAR]
[N1:PEM-LAB_PURPLEAIR_PM_1_0]
[N1:PEM-LAB_PURPLEAIR_PM_2_5]
[N1:PEM-LAB_PURPLEAIR_PM_10]
# Legacy channels from the initial EPICs softIoc implementattion
# are listed below. These channels are copies if the channels listed above
#
# The EPICS softIoc service is managed by the systemd softEnvIOC.service
# When ready this service can be removed, and these channels deleted.
#
[N1:ENV-PT1000_TEMP_INMON]
[N1:ENV-HUMIDITY_INMON]
[N1:ENV-PRESSURE_INMON]
[N1:ENV-HTU210F_TEMP_INMON]
```

If there is no `edc.ini` file present, this file can be copied into the `/etc/advligorts` directory on the N1FE1 machine. However is we want to update the service, then we only need to copy the channel names (including the `[]`) into the excisting file.

We will use symbolic links to let the `standalone_edc` and the `daqd` work together. The `standalone_edc` service get all the sloe EPICS channels, are per edc.ini file. Important parameter is the **dcuid=52** entry, as this is the reserved dcuid for the standalone_edc service (real-time models have their own, NOT 52 and >20 value).

At ANU we have the N1FE1 front-end machine and the N1FB10 daq/framebuilder machine, which are on the same network and have shared network drives. We will place the .ini file in the following location

`$ cp ini/torpedo_env_ctrl_ini_content.txt /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini`

The name refers to `<IFO><FRONT_END>_EDC.ini`, as there can only be one `standalone_edc` service per front-end. However we can have multiple front-ends. However when this file already excist, we add the channel names to this file.

To link this file to the standalone_edc service, we create a symlink in the `/etc/advligorts/` to that file.
On the `n1fe1` front-end we do:

`$ sudo ln -s /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini /etc/advligorts/edc.ini`
  
To restart `the standalone_edc` to take this into effect we do:

`$ sudo systemctl restart rts-edc.service`

This makes sure that the `daqd` service will receive the data.

To make the `daqd` service recognise and record the data, we will need to add the `N1FE1_EDC.ini` to its `master` file.

We need to login to the daqd machine (can be the front-end on a single machine setup like the cymac systems). In our case we log into the `n1fb10` machine.

The easiest way is the following:

```
controls@n1fb10:~$ cd /etc/advligorts/
controls@n1fb10:/etc/advligorts$ ls -al
total 52
-rw-r--r--   1 root root  5733 Jul 14 09:56 daqdrc
-rw-r--r--   1 root root    16 Aug 13 16:17 env
lrwxrwxrwx   1 root root    37 Oct 31  2020 master -> /opt/rtcds/anu/n1/daq0/running/master
-rw-r--r--   1 root root    23 Oct 17  2020 subscriptions.txt
-rw-r--r--   1 root root  1879 Nov 17  2020 systemd_env
lrwxrwxrwx   1 root root    48 Aug  4  2020 testpoint.par -> /opt/rtcds/anu/n1/target/gds/param/testpoint.par
controls@n1fb10:/etc/advligorts$controls@n1fb10:/etc/advligorts$ cat master
# NO EMPTY LINES
#
# INI FILES -----------------------------
#/opt/rtcds/anu/n1/target/n1iopfe1/param/N1IOPFE1.ini
#/opt/rtcds/anu/n1/target/n1isisc/param/N1ISISC.ini
/opt/rtcds/anu/n1/chans/daq/N1IOPFE1.ini
/opt/rtcds/anu/n1/chans/daq/N1ISISC.ini
# SLOW CONTROL INI FILES (ACROMAG or RPI) -----------
# Required so the daqd knows about them
/opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini
#
# PAR Files -----------------------------------------
#/opt/rtcds/anu/n1/target/n1iopfe1/param/tpchn_n1iopfe1.par
#/opt/rtcds/anu/n1/target/n1isisc/param/tpchn_n1isisc.par
/opt/rtcds/anu/n1/target/gds/param/tpchn_n1iopfe1.par
/opt/rtcds/anu/n1/target/gds/param/tpchn_n1isisc.par
controls@n1fb10:/etc/advligorts$ nano master
controls@n1fb10:/etc/advligorts$
```
In the above the `/opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini` has already been added, but points to the `N1FE1_EDC.ini` file created earlier. Also note that the `master` file points to a specific location, although not required, it keeps a slight resemblems to the LIGO sites (which can sometime be a good and a bad thing).

When the `master` file has been updated we can restart the `daqd` service

`$ sudo systemctl restart rts-daqd.service`

and we can check it with

`$ sudo journalctl --unit rts-daqd.service`

# Check is all is working

On the workstations, we can use `dataviewer` or `ndscope` to see if we can access the new channels. An easy way is

`$ ndscope N1:PEM-LAB_PT1000_TEMP_C`

(make sure you are inthe right <IFO> environment (at ANU a1 or n1!?)
