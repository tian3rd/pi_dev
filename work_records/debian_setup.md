## Install and Setup Debian

### Steps

#### Install [Debian-11.1.0-amd64-netinst.iso](https://www.debian.org/download) (minimal base system - without GUI)

0. Prepare the USB drive for Debian (provided in the black thumb drive). Plug in the USB drive to the new 5K beast.
1. Press `F11` to enter the `BIOS` setup screen when turning on the beast.
2. Change the boot order: #1 should be the USB hard drive
3. Save settings and exit
4. For most part, select the default options using 'Graphical install' option. Refer to this link for more details: https://tecadmin.net/how-to-install-debian-11/
   - Hostname: `n1fe0`
   - Domain name: leave empty
   - Password: `$4cgp$` (without ``)
   - Full name for the new user: bram
   - Partition method: 'Guided - use entire disk'
   - Select the attached Samsung SSD 500G
   - Partitioning scheme: 'Separate /home, /var, and /tmp partitions'
   - Finish partitioning and write changes to disk
   - Choose software to install: 'standard system utities'
   - Install the GRUB boot loader: yes
5. Remove the USB drive after installation, and change the boot order back to # 1 Samsung hard drive.

#### Using the Debian GNU/Linux 11

0. Update the `apt` sources configurations
   - `su -` first to change to `root` user first
   - `nano /etc/apt/sources.list`: overwrite the default sources.list with the following and restart after saving the file: `reboot`

```
deb http://deb.debian.org/debian bullseye main contrib non-free
deb-src http://deb.debian.org/debian bullseye main contrib non-free

deb http://deb.debian.org/debian-security/ bullseye-security main contrib non-free
deb-src http://deb.debian.org/debian-security/ bullseye-security main contrib non-free

deb http://deb.debian.org/debian bullseye-updates main contrib non-free
deb-src http://deb.debian.org/debian bullseye-updates main contrib non-free
```

1. Install the `openssh-server` package
2. Set up controls user account
   (For details, please follow instructions step 2 to step 5 in the file from sharepoint: https://anu365.sharepoint.com/sites/gw-torpedo/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2Fgw%2Dtorpedo%2FShared%20Documents%2Fcds%2Fn1fe1%2Fdebian%2Dbuster%2Dinstall%2Dsetup%2Etxt&parent=%2Fsites%2Fgw%2Dtorpedo%2FShared%20Documents%2Fcds%2Fn1fe1 )

### Trouble shooting

1. When installing debian, pull out the network cable out and _don't_ select any network mirror such as deb.debian.org. We'll add it later when we finish our debian minimal base system. The reason for doing this is that the adding the mirror will install the full version and when we reboot, the newly installed debian system will go into black screen after the flash screen. (Don't know why it acts like this, but as a compromise, we'll add the mirror later when we finish our debian minimal base system which only has the termial interface and can be successfully booted after installation.)
