> Start date: 22/11/2021

## Work Records

### Week 0

Date: 22/11/2021 - 28/11/2021

Monday
Prep work. Got a box of accessories, including:

- Breadboard (2x)
-

### Week 1

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

### Week 2

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
