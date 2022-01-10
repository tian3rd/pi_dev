## RPI setup to use lsc vga control service

It uses up to 4 Acromag XT1111 devices to control the gains and filters, and read back the values.

For local testing purposes, refer to this [readme file](../../readme.md) for more details in prepartion and setting up environment, etc. Right now we are testing two of the units at the same time using this interface:

![xt1111_interface](../../screenshots/2021-12-22-130928_589x330_scrot.png)

### Installation

> Assume now you're in the directory of `softioc` for the following `bash` commands.

There will be up to 4 directories, which are used as follows:

- **ini** -
  This hold the standalone_edc edc.ini file including the header details. If there is already a standalone_edc service running then you only have to manually copy the channel names into the excisting edc.ini file.

- **medm** -
  This holds the mdem interface file for the `lsc_vga_ctrl` service. Once the service starts, use `medm lsc_vga_ctrl/medm/devices.adl` to interact with the service via this interface.

- **python** -
  This hold the python implementations of the service. This can be based on the EPICS softIoc server or the python based pcaspy implementation. The remained of this installation instruction is based on the pcaspy SimpleServer implementation.

- **systemd** -
  This hold the files for installation of the python script to run and managed by the OS systemd service. This will help keep the python implementation operational.

```bash
# Installation
sudo cp lsc_vga_ctrl/systemd/lsc_vga_ctrl_service.service /etc/systemd/system/
#
# change the permission of the file to 644
sudo chmod 664 /etc/systemd/system/lsc_vga_ctrl_service.service
#
sudo mkdir /usr/local/lib/lsc_vga_ctrl_service
sudo cp lsc_vga_ctrl/python/lsc_vga_ctrl.py /usr/local/lib/lsc_vga_ctrl_service/lsc_vga_ctrl.py
sudo cp lsc_vga_ctrl/python/busworks.py /usr/local/lib/lsc_vga_ctrl_service/busworks.py
#
# make dir for lsc_vga_ctrl to store ini files, etc
mkdir -p /opt/rtcds/anu/n1/softioc/lsc_vga_ctrl/ini/
# change ownership of folder lsc_vga_ctrl to controls:controls to avoid permission denied problem if you create folder using sudo (root)
# sudo chown controls:controls /opt/rtcds/anu/n1/softioc/lsc_vga_ctrl/
#
# location of this file
# /etc/systemd/system/lsc_vga_ctrl_service.service
#
# enable with
sudo systemctl enable lsc_vga_ctrl_service.service
#
# start with
sudo systemctl start lsc_vga_ctrl_service.service
#
# check status with
sudo systemctl status lsc_vga_ctrl_service.service
```

### Recording the EPICS channels

The EPICS channels need to be obtained by the `standalone_edc` service on one of the front-end machines (`N1FE1` or `N1FE0`).

In the **ini** directory there is a file `lsc_vga_ctrl_ini_content.txt`. the content of the file needs to be copied into the `edc.ini` file for the `standalone_edc` service.

```
# Auto generated file by lsc_vga_ctrl.py
# at 2021-12-21 16:25:46
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
[N1:LSC-VGA_CHAN_0_GAINS]
[N1:LSC-VGA_CHAN_0_FILTERS]
[N1:LSC-VGA_CHAN_0_GAINS_RB]
[N1:LSC-VGA_CHAN_0_FILTERS_RB]
[N1:LSC-VGA_CHAN_0_GAINS_ERROR]
[N1:LSC-VGA_CHAN_0_FILTERS_ERROR]
[N1:LSC-VGA_CHAN_0_FILTER04]
[N1:LSC-VGA_CHAN_0_FILTER05]
[N1:LSC-VGA_CHAN_0_FILTER06]
[N1:LSC-VGA_CHAN_1_GAINS]
[N1:LSC-VGA_CHAN_1_FILTERS]
[N1:LSC-VGA_CHAN_1_GAINS_RB]
[N1:LSC-VGA_CHAN_1_FILTERS_RB]
[N1:LSC-VGA_CHAN_1_GAINS_ERROR]
[N1:LSC-VGA_CHAN_1_FILTERS_ERROR]
[N1:LSC-VGA_CHAN_1_FILTER04]
[N1:LSC-VGA_CHAN_1_FILTER05]
[N1:LSC-VGA_CHAN_1_FILTER06]
[N1:LSC-VGA_CHAN_2_GAINS]
[N1:LSC-VGA_CHAN_2_FILTERS]
[N1:LSC-VGA_CHAN_2_GAINS_RB]
[N1:LSC-VGA_CHAN_2_FILTERS_RB]
[N1:LSC-VGA_CHAN_2_GAINS_ERROR]
[N1:LSC-VGA_CHAN_2_FILTERS_ERROR]
[N1:LSC-VGA_CHAN_2_FILTER04]
[N1:LSC-VGA_CHAN_2_FILTER05]
[N1:LSC-VGA_CHAN_2_FILTER06]
[N1:LSC-VGA_CHAN_3_GAINS]
[N1:LSC-VGA_CHAN_3_FILTERS]
[N1:LSC-VGA_CHAN_3_GAINS_RB]
[N1:LSC-VGA_CHAN_3_FILTERS_RB]
[N1:LSC-VGA_CHAN_3_GAINS_ERROR]
[N1:LSC-VGA_CHAN_3_FILTERS_ERROR]
[N1:LSC-VGA_CHAN_3_FILTER04]
[N1:LSC-VGA_CHAN_3_FILTER05]
[N1:LSC-VGA_CHAN_3_FILTER06]
```

### Miscellaneous

1. The graph for connections of gains and filters on the isc whitening board: [here](../../isc_whitening_filter_D1001530_v5.pdf)

   - BI0 -> i0 -> D0 -> A1 (Gain: 24dB)
   - BI1 -> i1 -> D1 -> A2 (Gain: 12dB)
   - BI2 -> i2 -> D2 -> A3 (Gain: 6dB)
   - BI3 -> i3 -> D3 -> A4 (Gain: 3dB)
   - BI4 -> i4 -> D4 -> A5 (Filter: PZ1)
   - BI5 -> i5 -> D5 -> A6 (Filter: PZ2)
   - BI6 -> i6 -> D6 -> A7 (Filter: PZ3)
   - BI7 -> LE
   - BO0 -> R0
   - BO1 -> R1
   - BO2 -> R2
   - BO3 -> R3
   - BO4 -> R4
   - BO5 -> R5
   - BO6 -> R6
   - BO7 -> R_LE

   I/O ports on XT1111:

   ```
   ch00 | ch01 | ch02 | ch03 ==> gains: 24dB | 12dB | 6dB | 3dB
   ch04 | ch05 | ch06 | ch07 ==> filters: f1 | f2 | f3 | LE (on/off)
   ch08 | ch09 | ch10 | ch11 ==> readbacks for gains
   ch12 | ch13 | ch14 | ch15 ==> readbacks for filters and LE
   ```

2. XT1111 input/output voltage.

   - Power supply voltage: 12-32V
   - Excitation voltage:
   - Inverse mode by default.
   -

3. Connect to XT1111 via static ip address.

   - To set a different ip address, use the windows client software.
   - Right now there are two testing acromag units with addresses: `192.168.1.100` and `192.168.1.101`.

4. About `busworks.py`.

   - To get the acromag XT1111 to sucessfully write to the registers, it should wait at least 20ms for the next opearation, which is implemented in the code using `sleep(self.dt)`.
   - The `busworks.py` module is used to read and write the acromag XT1111 registers via the modbus protocol.

5. About `lsc_vga_ctrl.py`.
   - In order for the system to load all required packages including `pcaspy`, set aside an extra second before initializing the server, which is implemented in the code using `sleep(1)`.
   - The channel name for indivisual filters from filter 1 to 3 is represented by `FILTER04` to `FILTER06` which is because they are connected to XT1111 i/o ports 04 to 06. (Will be changed to `FILTER01` to `FILTER03` in the future)
   - When the script is running, we need to frequently monitor any incoming changes and respond accordingly, which is implemented by `server.process(0.1)`.
   - We don't need to do all the read operations in the while loop, but instead, whenever there's a change to write, we read the updated data after the write operations to reflect the newest changes.
