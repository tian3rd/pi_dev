"""
A generic python PID controller using EPICS.

It follows the following usage:
 python CDS_PID.py [-h] [--PIDfilt PID_filter_prefix] [--input input]

 example:
 python CDS_PID.py --PIDfilt ISC-LASER_D_TEMP_ --input LSC-PDH_FAST_C_LF_NORM_MON  --output ISC-LASER_D_CRYSTAL_TEMP_VOLT &> /dev/null


It expects the PID filter to have the following EPICS channels:
 > *INMON - Input monitor, at 10 Hz (optional).
 > *IN_EN - Engage the PID filter input.
 > *SETPOINT - The PID controller set point.
 > *KP - The proportional gain.
 > *KI - The integral gain.
 > *KD - The derivative gain.
 > *RESET - A boolean flag to reset the PID memory.
 > *PID_PAUSE - Freeze, the current PID controller output.
 > *LIM_EN - Engage limiting for the PID output.
 > *LIM_UPR - Upper limit for PID output.
 > *LIM_LWR - Lower limit for PID output.
 > *FBMON - A monitor for the PID controller's feedback.
 > *OUT_EN - A boolean flag to indicate if the ouput is engaged.
 > *FB - The feedback output from the PID controller (optional).

The following Python libraries are required:
 > simple_pid
 > ezca
 > warnings
 > argparse

Author: Nathan Holland.
Contact: nathan.holland@anu.edu.au
Date: 2018-11-05

Modified: 2018-11-05
"""
#-------------------------------------------------------------------------------
#Imports:
from simple_pid import PID;
from ezca import Ezca;
from warnings import warn;
import argparse;
#-------------------------------------------------------------------------------
#Script Configuration:
_pid_init_config = {"Kp" : 0.0, "Ki" : 0.0, "Kd" : 0.0, "setpoint" : 0.0,
	"sample_time" : 0.1, "output_limits" : (-10.0, 10.0)}
	#Initial configuration for the PID controller.
_version = "0.0.2"; #Version (major, minor, revision).
#-------------------------------------------------------------------------------
#Static, common:
__all__ = []; #Nothing to see here.
#
_in_dflt = "INMON"; #The DEFAULT input to the PID controller.
_in_engage = "IN_EN"; #The input engage channel.
_reset = "RESET"; #The memory reset flag for the PID controller.
_setpoint = "SETPOINT"; #The setpoint for the PID controller.
_kp = "KP"; #The proportional gain.
_ki = "KI"; #The integral gain.
_kd = "KD"; #The derivative gain.
_lim_engage = "LIM_EN"; #The limit engage channel.
_lim_upper = "LIM_UPR"; #The upper limit.
_lim_lower = "LIM_LWR"; #The lower limit
_pause = "PID_PAUSE"; #The PID feedback engage method.
_fbmon = "FBMON"; #The feedback monitor channel.
_out_engage = "OUT_EN"; #The output engage channel.
_fb_dflt = "FB"; #The DEFAULT feedback channel.
#
_epics_write_kwargs = {"monitor" : False}; #Don't print the write to stdout.
#
_script_name = "CDS_PID.py";
_script_description = "A generic python PID filter, backend, for slow CDS " + \
	"PID filters."; #A description of the scripts function.
_pidfilt_help = "A string indicating the channel prefix to use. " + \
	"For example if the desired channels are A1:ISC-LASER_D_TEMP_* then " + \
	"the prefix to use is <ISC-LASER_D_TEMP_>. The IFO indicator can be omitted.";
	#Help for the --PIDfilt argument.
_input_help = "(Optional) A string indicating the input channel to use. " + \
	"For example if the desired input channel is " + \
	"A1:LSC-PDH_ERR_D_LF_NORM then the input channel is " + \
	"<LSC-PDH_ERR_D_LF_NORM>."; #Help for the --inputs argument.
_output_help = "(Optional) A string indicating the output channel to use. " + \
	"For example if the desired output channel is " + \
	"A1:ISC-LASER_D_XL_TEMP then the output channel is " + \
	"<ISC-LASER_D_XL_TEMP>."; #Help for the --output argument.
#
#-------------------------------------------------------------------------------
#Define the argument parser.
_parser = argparse.ArgumentParser(prog = _script_name,
	description = _script_description); #The argument parser.
_parser.add_argument("--version", action = "version", version = _version);
	#Add the version argument.
_parser.add_argument("--PIDfilt", help = _pidfilt_help, nargs = 1, type=str,
	required = True); #Add the PIDfilt argument.
_parser.add_argument("--input", help = _input_help, nargs = 1, type = str,
	required = False, default = None); #Add the input argument.
_parser.add_argument("--output", help = _output_help, nargs = 1, type = str,
	required = False, default = None); #Add the output argument.
#-------------------------------------------------------------------------------
def main(channels_prefix, input_channel, output_channel):
	"Performs the main looping."
	#PID Initialisation:
	pid = PID(**_pid_init_config); #Create the PID controller.
	pid.auto_mode = True; #Output of the PID controller is engaged.
	#
	#EPICS Initialisation:
	epics_inout = Ezca(); #Make a separate connection to the input.
	epics_inout.connect(input_channel); #Check connection to the input.
	epics_inout.connect(output_channel); #Check connection to the output.
	#
	epics_access = Ezca(prefix = channels_prefix);
		#Create the epics access object.
	epics_access.connect(_in_engage);
		#Check the connection to input engage.
	epics_access.connect(_reset); #Check the connection to the reset.
	epics_access.connect(_setpoint); #Check the connection to the setpoint.
	epics_access.connect(_kp);
		#Check the connection to the proportional gain.
	epics_access.connect(_ki);
		#Check the connection to the integral gain.
	epics_access.connect(_kd);
		#Check the connection to derivative gain.
	epics_access.connect(_lim_engage); #Check connection to limit engage.
	epics_access.connect(_lim_upper); #Check connection to the upper limit.
	epics_access.connect(_lim_lower); #Check connection to the lower limit.
	epics_access.connect(_fbmon); #Check the connection to feedback monitor.
	epics_access.connect(_out_engage);
		#Check the connection to output engage.
	#If the channels aren't available then let ezca throw an error.
	#
	while True:
		#Loop forever.
		#Input switching -
		if epics_access.read(_in_engage):
			error = epics_inout.read(input_channel);
				#Collect the input.
		else:
			error = 0.0; #No filter input otherwise.
		#
		#Filter memory clearing -
		if epics_access.read(_reset):
			pid = PID(**_pid_init_config);
				#Reset the PID controller.
		else:
			pass;
		#
		#Set the PID controller values -
		pid.setpoint = epics_access.read(_setpoint); #Set the set point.
		pid.Kp = epics_access.read(_kp); #Set the proportional gain.
		pid.Ki = epics_access.read(_ki); #Set the integral gain.
		pid.Kd = epics_access.read(_kd); #Set the derviative gain.
		#
		#Set controller limits -
		if epics_access.read(_lim_engage):
			pid.output_limits = (epics_access.read(_lim_lower),
				epics_access.read(_lim_upper));
				#Set the ouput limits.
		else:
			pid.output_limits = (None, None); #No limits.
		#
		#Set PID output -
		if epics_access.read(_pause):
			pid.auto_mode = False; #Don't engage the PID controller.
		else:
			pid.auto_mode = True; #Engage the PID controller.
		#
		#PID feedback -
		feedback = pid(error); #Get the PID feedback.
		epics_access.write(_fbmon, feedback, **_epics_write_kwargs);
			#Write to the feedback monitor channel, no printing.
		#
		#Output switching -
		if epics_access.read(_out_engage):
			epics_inout.write(output_channel, feedback,
				**_epics_write_kwargs);
				#Write the feedback, no priniting.
		else:
			epics_inout.write(output_channel, 0.0,
				**_epics_write_kwargs);
				#Write nothing, no priniting.
		#
#
#-------------------------------------------------------------------------------
#Initialisation - pass arguments:
_passed_args = _parser.parse_args(); #Pass the arguments.
_args = vars(_passed_args); #Convert the namespace object to a dict.
#Package arguments:
_prefix = _args["PIDfilt"][0]; #Package prefix name.
if _args["input"][0] is None:
	_in_chnl = _prefix + _in_dflt; #Default value
else:
	_in_chnl = _args["input"][0]; #User specified.
#
#Package input name.
if _args["output"][0] is None:
	_fb_chnl = _prefix + _fb_dflt; #Default value.
else:
	_fb_chnl = _args["output"][0]; #User specified.
#
#Package feedback name.
#Call main:
main(_prefix, _in_chnl, _fb_chnl); #Run the main part of the script
#-------------------------------------------------------------------------------
#END.
