> Start date: 22/11/2021

## Work Records

### Full Time @ CGA

#### Week 0 (21/02/2022 - 27/02/2022)

Friday 25/02/2022

0. Assemble RBOOM
1. LTC1151 x2 && VGA resistor bank x10 ordered from mouser
2. Sanity check for RBOOM to record data (forward data to remote server)
3. Inquirey about 20s mechanical filter from RShake

#### Week 1 (28/02/2022 - 06/03/2022)

Monday 28/02/2022 0. Understand the issue with `systemtcl` service failed issue (NTP service)

1. Read the documentation about how udp data output works for RBOOM
2. Set up data forwarding to local network devices
3. PEM box restart with connection to the acromag temperature sensor
   - Check the status of voltage every 15 - 30 minutes to see if it drops from 24V to 10.5V which is lower than the excitation voltage of the acromag units, thus shutting those units down.

Tuesday 01/03/2022

1. Check PEM box again, and it turns out if the temperature sensor (10.0.0.8) is connected, when trying to access one of the acromag units (BIO0-2 10.0.0.5-10.0.0.7, ADC0-2 10.0.0.2-10.0.0.4), the voltage will randomly drop to 10.5V and shuts down the acromag units.
2.

### Summer Project (Nov 2021 - Jan 2022)

#### Week 0

Date: 22/11/2021 - 28/11/2021

Monday
Prep work. Got a box of accessories, including:

- Breadboard (2x)
-

#### Week 1

Date: 29/11/2021 - 04/12/2021

Monday 0. Modify the python script of XT1541-000 DAC to set up the new AcroMag XT1111-000.

1. Configure I/O ports of XT1111-000 using pymodbus package.
2. Read the documentation of XT1111-000.

Tuesday

1. Attend Johannes's talk on NEMO at Stromlo Lab.
2. Debug the script to control the on/off of the i/o ports.
3. Try to connect the i/o port to breadboard, but it has a problem: on/off can't switch once it's connected. For example, in a reverted situation (default), it's 4.5V as a default for i/o port 00, then if I connect i/o 00 to breadboard with 2 1k reistors, and wire to RTN (ground), then it's automatically turned on on the screen, and the voltage betwwen i/o 00 and RTN is 0.7V. There's no way to control it to be back at 4.5V.
   1. Maybe there's internal resistors in XT1111?

Wednesday

1. Troubleshoot the problem of can't turn on/off the i/o port when it's connected to breadboard.

   1. Connect one end to excitation voltage, and the other to the i/o port. So when in default inverted, the i/o port has 4.5V, and the voltage different is 0.5V which is not enough to light up the LED; when i/o 00 is turned on, then the voltage of i/o drops to 0V, so the difference is 5V where there's current flowing through the LED, so it's turned on.
   2. ![img](https://cdn-std.droplr.net/previews/ySilCv.preview_medium.png)

2. Sanity check of the vacuum gauge using the pfeiffer_tpg261_service.py script.

   1. the usb to serial cable may cause the reading fo the device to be wrong.

3. Read the docs of `pcaspy` package.

Thursday

1. Check the readback voltages from i/o ports using the voltage from i/o ports 00 - 07 (gains and filter): e.g., connecting the output wire from port 00 to port 08, so if we turn 00 on, then the voltage on 08 will be set as low, so 08 will also be turned on; if we turn 00 off, then the voltage on 08 will be set as high, so 08 will also be turned off. We can get the readbacks to make sure that we set the gains and filters as we want.

2. Debug the simple read operations with `pcaspy` package. Add three simple read attributes: GAINS, FILTERS, and READBACKS.

Friday

0. Update interval? If we toggle the i/o port too fast, then we may not be able to update the i/o status in time.

   - Solution: add a delay between each toggle using time.sleep(). The interval is not tested, and for now it's set to 0.05s.

1. Modify the MEDM interface for read and write operations.

2. Add slider bar for easier adjustment of gains.
   - Problem: it has a bug of not setting the value when the slider is exactly divisible by 3.

#### Week 2

Monday

1. Add 8 indicators and corresponding data channels to show status of the i/o ports 00 to 07. (Just like the window client red/grey port indicators.)

   - GAIN_CH00 to GAIN_CH03
   - FILTER_CH04 to FILTER_CH06
   - LE_CH07

2. Refactor the read operations inside the driver.

Tuesday

1. Try to use click event to toggle the red/black indicator ovals for channel 00 to 07.

   - `Oval` doesn't work: not associated functionalities
   - `Slider bar` as a compromise: only has two values of 0 and 1 for toggling between red and black.
   - `Choice button` seems more appropriate for binary choices.

2. Refactor code in `busworks_xt1111.py` and `xt1111_service.py`

3. Discuss with Sheon on how to improve the interface.

Wednesday

1. Fix bugs of not updating the status in real time
2. Rearrange the elements in the interface
3. Add indicators for readback channels; add choice buttons for filter channels
4. Add start up instructions

#### Week 3

Monday

1. Fix bugs of `enable` indicator
2. Discuss with Sheon on how the interface components are arranged.
3. Create new interface for xt1111 in file `xt1111.adl`.
4. Look up the documentation for how to set static ip addresses for the acromag devices. (Currently it requires manual configuration using the windows client. Once it is set, it won't change back to the default.)
5. Update readme bugs and progesses.

Tuesday

1. Fix bugs: a. filter btn toggling back; b. error message starting up medm.
2. Update interfaces with reference display btn, warning for readbacks.
3. Discuss with Bram about the interface.
4. Use the new Samsung UR55 4K monitor for Raspberry Pi.
5. Add comments in `xt1111_service.py` script.

Wednesday

1. Work on implementing the bus service in folder `softioc/lsc_vga_ctrl` based on the discussion with Bram yesterday.
2. Write the draft `lsc_vga_ctrl.py` for testing tomorrow.
   - Generate ini file
   - Start server and keep reading the busDB
   - (Haven't got a chance to test it yet due to power outage of the desk power supply.)

Thursday

1. Relocate to another desk with power supply
2. Install debian on the beast: it won't go into the GUI after installation :(
3. Debug the script and fix bugs, now it's working as expected for one xt1111 unit. Got another one and a switch to test for tomorrow.
   - Fix displaying issues of `devices.adl` (use full channel names!)
   - Fix typos and bugs of `lsc_vga_ctrl.py`

Friday

1. Install debian 11.1.0 on the new beast
2. Draft a documentation for installing and setting up the debian.

#### Week 4

Monday

1. Adjust the medm interface to show readback warning dashed box.
2. Start testing the 2nd acromag device connecting to a switch (Linksys SD205): each device connects to the switch port instead of using a daisy chain setup.
3. Set up debian 11 on `op6anu` together with Avanish. Refer to [Installing LIGO RT Front.pdf](./Installing%20LIGO%20RT%20Front.pdf) for configuration details.

Tuesday

1. Test an acromag DAC device for differential voltage signal with Sheon, Deon, and Avanish. The problem is that the DAC device is not showing -10 to 10V range signal if we have -6.6V to 6.6V input. The manual says that the unused ports should not be floating, so we connenct all negative ports to ground together with RTN.
2. Continue setting up the debian on `op6anu` with Avanish.

Wednesday

1. Wrap up documentation for the first few weeks work on acromag XT1111.
2. Write `lsc_vga_ctrl_service.service` for systemd (use `torpedo_env_ctrl_service.service` as a template).
3. Add a simple readme file for `lsc_vga_ctrl` services.

#### Week 5

#### Week 6

Wednesday

1. Include error channels in the database for future logging and error handling.
2. Modify the interface to show error messages for gains and filters.

Thursday

1. Refactor code
   - To only read when writing changes in gains/filters.
   - To clean up the code and fix typos
2. Update file and channel names

Friday

1. Debug `lsc_vga_ctrl_service.service` on startup.

#### Week 7

Monday

1. Set up devices at home office.
2. Test XT1111 with LED on the breadboard.
3. Clean up code and add bullet points to readme file.

## Q&A

0. How do I set up the environment?

   - Physical devices:
   - Python env:

1. How do I talk to BusWorks?

   - BusWorks model manual:
   - Initialization and configuration:

2. How to connect the raspberry pi with the XT1111-000?

   - Modbus TCP

3. How to read signal and write signals to the device?

   - Using the pymodbus interface:

4. What is an _EPICS_?

   - https://epics.anl.gov/index.php

5. How to read the vacuum gauge?

   - https://www.pfeiffer-pms.com/en/products/tpg261/

6. What is `pcaspy` and how to use it?

   - Docs: https://pcaspy.readthedocs.io/en/latest/
   - https://github.com/paulscherrerinstitute/pcaspy
