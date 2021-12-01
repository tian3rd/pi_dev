Raspberry Pi

## Cookbook

2.1 Finding IP address

    - `hostname -I`
    - `ifconfig`

2.2 Setting a static IP address

    - `sudo vim /etc/dhcpcd.conf`

    ```
    interface eth0
    static ip_address=192.168.1.210/24
    static routers=192.168.1.1
    static domain_name_servers=192.168.1.1
    ```

    - `sudo reboot` or `sudo systemctl start dhcpcd.service` to make the changes take effect

2.3 Setting the network name of Raspberry Pi

    - 1. `sudo vim /etc/hostname` 2. `sudo vim /etc/hosts`
    - `sudo raspi-config` for an interative way to set the network name

2.7 Controlling Pi remotely with ssh

    - Enable the ssh on Pi: `sudo raspi-config` or use Preferences -> Raspberry Pi Configuration -> Interfaces -> SSH -> Enabled
    - `ssh 192.168.xxx.xxx -l pi`

2.8 Controlling Pi remotely with VNC

    - Turn the VNC on: `sudo raspi-config` or use Preferences -> Raspberry Pi Configuration -> Interfaces -> VNC -> Enabled
    - Install RealVNC on Mac: `brew install --cask vnc-viewer`

## Miscellaneous

1. The operating voltage of the GPIO pins is 3.3v with a maximum current draw of 16mA.

2. When I set up the static IP for `eth0`, Pi will not be able to connect to the internet.

   - https://raspberrypi.stackexchange.com/questions/108592/use-systemd-networkd-for-general-networking/108593#108593
   - https://raspberrypi.stackexchange.com/questions/118544/how-to-config-static-ip-on-eth0-but-keep-wlan0-dynamic
