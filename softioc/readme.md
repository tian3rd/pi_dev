## Deployment of the SERVICES

_Use `cat /etc/fstab` to check the file system configuration_
The way it works is that,
first, we copy all the related scripts and services to the nas drive (ANU CDS Network `cdsnas0` and ANU CDS NAS - Synology `cdsnas1`),
second, we use the local `/etc/fstab` configuration to mount the nas drive to the local corresponding directories (i.e., `/opt/rtcds`, `/opt/rtapps/`, and `/ligo`)
then, we can run the services because all the required files are on local machine.
In this way, all the workstations (op5anu, rpidev, seimodbus0 all have the synchronous files and scripts)

```bash
# mount network driver onto local disk based on the config in /et/fstab
sudo mount -a
```

_Use of `n1sitemap.sh` to launch the medm interface for all services_ (use `which n1sitemap.sh` to check the path)
E.g., to get the status of the Trillium sensor, `ISI -> T240 Align & Shape -> T240 A/B/C` to bring forward the overview interface for zeroing, and data readout (ISI_T240_OVERVIEW.adl).

_IP, IM, PM_

_Run seimodbus0 services_
IP: 192.168.1.87
to access the service, use `ssh seimodbus0`
Ensure that the NAS drives are mounted locally on this rpi. If not, check the `/etc/fstab` and mount it. Double check that it's mounted with the command `mount`. Then restart the service with `sudo systemctl restart n1seimodbus0-IOC.service`, and the ISI_T240_OVERVIEW.adl will be displayed with the status of the sensor: U, V, W, Pressure, Temperature, velocity, etc. Use auto zero to calibrate the U, V, W channels. The maximum for them is +/- 2.5 out of +/- 10. It will drift with time, so when it's over +/- 2.5, we need to manually zero it.

_Check hosts on the network_
Use `cat /etc/hosts`.

_Why does the rpi `seimodbus0` see the 8 acromag units while others can't?_
So the network interface is specified in the file `/etc/network/interfaces`, and the file inside the dir `/etc/network/interfaces.d` can be used to tell the os how to go to `10.0.0.x` (acromag units from `10.0.0.2` to `10.0.0.8`):

```
auto eth0:1
allow-hotplug eth0:1
iface eth0:1 inet static
    address 10.0.0.1
    netmask 255.255.255.0
```
