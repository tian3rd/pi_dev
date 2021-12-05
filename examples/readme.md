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

3.14 Changing file permissions

    - `sudo chmod +x /home/pi/Desktop/my_script.sh`
    - `u` for user, `g` for group, `o` for others; `a` for all; `+x` for executable; `-x` for non-executable; `+w` for writable; `-w` for non-writable; `+r` for readable; `-r` for non-readable;

3.15 Changing file ownership

    - `sudo chown pi:pi /home/pi/Desktop/my_script.sh`

3.16 Making a screen capture

    - `scrot -d 5 /home/pi/Desktop/screenshot.png` for delaying 5 seconds
    - `scrot -s` for specific area

3.17 Installing/removing software with apt-get

    - `sudo apt-get install software`
    - `sudo apt-get update`
    - `sudo apt-get remove software`

3.23 Running a program or script automatically on startup

    - `sudo vim /etc/rc.local`
    - Add the following line: `/home/pi/Desktop/my_script.sh &` after the first block of comment lines that start with `#`. The `&` is to run the script in the background, otherwise RPi will not boot.

3.24 Running a program or script automatically as a service

    - Debian Linux uses a dependency-based mechanism to automatically run commands at startup.
    - Create an `init` in the folder of `/etc/init.d`: `sudo vim /etc/init.d/my_script.sh`
    - Then make the script executable: `sudo chmod +x /etc/init.d/my_script.sh`
    - Tell the system to run the script at startup: `sudo update-rc.d my_script.sh defaults`:
    - Use `sudo update-rc.d my_script.sh remove` to remove the script from startup.
    - Use `/etc/init.d/my_script.sh start` to test the script, and `/etc/init.d/my_script.sh stop` to stop it, `/etc/init.d/my_script.sh restart` to restart it, and `/etc/init.d/my_script.sh status` to check the status.

3.25 Running a program or script automatically at regular intervals

    - `sudo crontab -e`
    - Add the following line: `*/5 * * * * /home/pi/Desktop/my_script.sh`
    - `sudo crontab -l` to check the crontab
    - `*/5 * * * * /home/pi/Desktop/my_script.sh` for every 5 minutes
    - `0 */1 * * * /home/pi/Desktop/my_script.sh` for every hour :00 time
    - `0 1 */1 * 1-5 /home/pi/Desktop/my_script.sh` for every workdays at 1:00 AM
    - `minute hour day month day-of-week command`
    - Use `;` to separate multiple commands

3.26 Finding things

    - `find / -name "*.txt"`
    - `fd pattern` recursively finds files matching the given pattern in the current directory and subdirectories

3.27 Using the command history

    - `history | grep "keyword"`
    - Each history has a number next to it, `!n` to run the command with the number `n`

3.28 Monitoring processor activity

    - Use `top` or `htop` to monitor the processes
    - Use `ps -ef | grep "keyword"` to find the process
    - Use `kill -9 pid` to kill the process
    - `sudo killall -9 "keyword"` to kill all processes with the keyword

## Miscellaneous

1. The operating voltage of the GPIO pins is 3.3v with a maximum current draw of 16mA.

2. When I set up the static IP for `eth0`, Pi will not be able to connect to the internet.

   - https://raspberrypi.stackexchange.com/questions/108592/use-systemd-networkd-for-general-networking/108593#108593
   - https://raspberrypi.stackexchange.com/questions/118544/how-to-config-static-ip-on-eth0-but-keep-wlan0-dynamic
