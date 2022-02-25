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
