"""
Doc String:
A simple, test, PID controller for the TorPeDO using the libraries:
 > simple_pid
 > ezca
It is currently targeted towards laser D.

Must be used in conjunction with a configured EPICS database.
Curretn testing uses the IOCLASERSERVO.db database and
ioclaserservo.cmd softIoc startup command

To start with no feedback print output run like:
 $ python a1laser.py &> /dev/null

Authors: Nathan A. Holland, Bram J. J. Slagmolen.
Created: 2018-10-30
Contact: bram.slagmolen@anu.edu.au

Modified: 2018-11-05
"""
#------------------------------------------------------------------------------
#Imports:
from simple_pid import PID
from ezca import Ezca
from time import sleep
import timeit;
#------------------------------------------------------------------------------
#Static, common:
_laser = 'D' #The laser of interest.
_channel_common = 'ISC-LASER_{0}_TEMP_'.format(_laser) #Common channel name
#------------------------------------------------------------------------------
#Script Configuration:
_pid_init_config = {'Kp' : 0.0, 'Ki' : 0.0, 'Kd' : 0.0, 'setpoint' : 0.0,
	'sample_time' : 0.04, 'output_limits' : (-10.0, 10.0)}
	#Initial configuration for the PID controller.
_kd_channel = _channel_common + 'KD' #EPICS channel for derivative gain.
_ki_channel = _channel_common + 'KI' #EPICS channel for integral gain.
_kp_channel = _channel_common + 'KP' #EPICS channel for proportional gain.
_setpoint_channel = _channel_common + 'SETPOINT'
	#EPICS channel for temperature set point.
_output_engage_channel = _channel_common + 'EN'
	#EPICS channel for output on/off toggling.
_input_channel = 'LSC-PDH_ERR_{0}_LF_NORM_MON'.format(_laser)
#_input_channel = 'ISC-FSS_LASER_A_SLOW_RB'
	#EPICS channel to get input from.
#_output_channel = _channel_common + 'FB' #EPICS channel to output to.
_output_channel = 'ISC-LASER_D_CRYSTAL_TEMP_VOLT' #EPICS channel to output to.
#------------------------------------------------------------------------------
#Initialisation - run once, at the start.
pid = PID(**_pid_init_config)
	#Initialise the PID controller.
_epics_kd = Ezca()
_epics_kd.connect(_kd_channel)
	#The channel access for the derivative gain
_epics_ki = Ezca()
_epics_ki.connect(_ki_channel)
	#The channel access for the integral gain
_epics_kp = Ezca()
_epics_kp.connect(_kp_channel)
	#The channel access for the integral gain
_epics_setpoint = Ezca()
_epics_setpoint.connect(_setpoint_channel)
	#The channel access for the set point information
_epics_engage = Ezca()
_epics_engage.connect(_output_engage_channel)
	#Channel acces for the output engage
_epics_in = Ezca()
_epics_in.connect(_input_channel)
#Getting Ezca error here.
#ezca.errors.EzcaConnectError: Could not connect to channel (timeout=2s): A1:LSC-PHD_ERR_D_LF_NORM
	#Channel access for input.
_epics_out = Ezca()
_epics_out.connect(_output_channel)
	#Channel access for output.
#------------------------------------------------------------------------------
#While loop - do this forever.
while True:
#_start = timeit.default_timer();
#for _ in range(10):
	#Set PID values:
	pid.Kd = _epics_kd.read(_kd_channel)
	pid.Ki = _epics_ki.read(_ki_channel)
	pid.Kp = _epics_kp.read(_kp_channel)
	pid.setpoint = _epics_setpoint.read(_setpoint_channel)
	#Output engage logic:
	output_engage = _epics_engage.read(_output_engage_channel)
		#Do 'expensive' read operation once.
	if output_engage  == 1:
		#PID controller is engaged.
		pid.auto_mode = True
	elif output_engage == 0:
		#PID controller is disengaged.
		pid.auto_mode = False
	else:
		#Output engage channel is ill conditioned, run next iteration.
		continue
	#
	#Error signal processing:
	error = _epics_in.read(_input_channel)
		#Read in the input, an error signal.
	feedback = pid(error) #Let the PID controller calculate the feedback.
#	sleep(0.05)
	_epics_out.write(_output_channel, feedback)
#_stop = timeit.default_timer();
#print("Time for 100 loops: {0}".format(_stop - _start));
#
#------------------------------------------------------------------------------
#End
