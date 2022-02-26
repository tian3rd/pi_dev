## [Raspberry Shake](https://raspberryshake.org/)

### Q & A

1.  `ntp.service` is loaded but failed to start.
    Description: use `systemctl status ntp` to check the status of network time protocol, but it shows "Active: failed". Use `systemctl` to check all services, and find out there are three network time services: `ntp.service`, `ntpd.service` and `ntpdate.service`.
    A: According to the [Raspberry Shake forum], there was a similar post: https://community.raspberryshake.org/t/ntp-failed-or-could-not-be-found/2172, and as answered by technical support

    > Executing that command gives me a failed status result, but the actual two services that control the NTP time synchronization services are, as shown in our manual here [NTP and GPS timing details — Instructions on Setting Up Your Raspberry Shake 2](https://manual.raspberryshake.org/ntp.html?#details-for-ntp-power-users: ntpdate, ntpd
    > If you execute a systemctl status with these two names, you will (should) get an “Active” response for both of them.

2.  Set up ntp server to [ANU NTP server](https://services.anu.edu.au/information-technology/infrastructure/domain-name-service/anu-ntp-time-servers)

    ```
    ntp1.anu.edu.au 	150.203.1.10
    ntp2.anu.edu.au 	150.203.22.28
    ```

    Use `ntpq -p` to check the status of ntp server.
    Or use `timedatectl status` to see if the system clock is synced.
    When modifying the `/etc/ntp.conf` file, use `sudo systemctl restart ntpd` to restart the ntp service.

3.  `ifup@wlan0.service` is loaded but failed to start.

4.  HDF channel for Raspberry Boom
    The data format is `{'HDF', 1645756851.585, -2609, -5155, ..., -800, -6391}`.

    - HDF communicates to the end users that the BOOm is a 100 sample per second (H), microbarometer (D), infrasound (F) monitor.
    - The second is the timestamp in epoch seconds, down to milliseconds.
    - The following 25 samples are the data values for the pressure.

5.  How are the data packets transferred?
    Indivisual data packets are sent to port 8888 on the Shake Pi computer by default.
    ```python
    import socket as s
    with open('/opt/settings/sys/ip.txt', 'r') as file:
        host = file.read().strip()
    port = 8888 # Port to bind to
    sock = s.socket(s.AF_INET, s.SOCK_DGRAM | s.SO_REUSEADDR)
    sock.bind((host, port))
    print "Waiting for data on Port:", port
    while 1: # loop forever
        data, addr = sock.recvfrom(1024) # wait to receive data
        print data
    ```

### Reference

1. [How to set up NTP service in Linux](https://timetoolsltd.com/ntp/how-to-install-and-configure-ntp-on-linux/)
2. [NTP not started on bootup](https://askubuntu.com/questions/954768/ntp-service-not-getting-started-on-bootup)
3. [Configure NTP using ntpd (in redhat)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/ch-configuring_ntp_using_ntpd)
4. [RShake NTP GPS timing](https://manual.raspberryshake.org/ntp.html?#ntp-and-gps-timing-details)
5. [Specifications for: Raspberry Boom (RBOOM) and 'Shake and Boom'
   (RS&BOOM)](https://manual.raspberryshake.org/_downloads/SpecificationsforBoom_SnB.pdf)
6. [Raspberry Shake station shake naming convention](https://manual.raspberryshake.org/stationNamingConvention.html)
7. [Raspberry Shake Data Producer UDP Port Output](https://manual.raspberryshake.org/udp.html)
