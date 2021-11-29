# ncal_wheel_ctrl

This is code for a Teensy 3.5 to control a servo motor to drive the Newtonian Calibraiton Wheel.

The Teensy is connected to a Respberry Pi which communicates with the Teensy. The RPI connects via EPICS and ASYN program.

There is an EPICS database to run in EPICS.

\> arduino
hold the Teensy 3.5 firmware code

\> epics

holds the EPICS database, .proto file and MEDM screen

\> ncalioc

Hold the EPICS IOC program compiled for the Teensy.

\> python

some serial testing programs


To start the EPICS IOC

  cd ncal_wheel_ctrl/ncalioc/iocBoot/iocncal_response

  ./st.cmd

To start the MEDM screen interface

  cd ncal_wheel_ctrl/epics

  medm -x ncal.adl

To add to the github, do the following sequence:
  git add -u	// add to the local staging area
  git commit -m "message"	// commit from staging area to the repo
  git pull	// to sync repo with local staging to check for conflict
  git push	// do the copy

