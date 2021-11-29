"""
A generic python PID controller using EPICS.

It follows the following usage:
 python CDS_PID.py [-h] [--PIDfilt PID_filter_prefix] [--input input_channel]
 [--output output_channel]

E.g:
 python CDS_PID.py --PIDfilt A1:ISC-LASER_D_TEMP_ --input 
 A1:LSC-PDH_ERR_D_LF_NORM --output A1:ISC-LASER_D_TEMP_VOLT &> /dev/null

It expects the PID filter to have the following EPICS channels:
 > *INMON - Input monitor, at 10 Hz (writes to).
 > *IN_EN - Engage the PID filter input (reads from).
 > *EXC - The excitation drive point (reads from).
 > *IN2 - The sum of INMON and EXC, if the input is engaged (writes to).
 > *SETPOINT - The PID controller set point (reads from).
 > *KP - The proportional gain (reads from).
 > *KI - The integral gain (reads from).
 > *KD - The derivative gain (reads from).
 > *RESET - A boolean flag to reset the PID memory (reads from).
 > *PID_PAUSE - Freeze, the current PID controller output (reads from).
 > *LIM_EN - Engage limiting for the PID output (reads from).
 > *LIM_UPR - Upper limit for PID output (reads from).
 > *LIM_LWR - Lower limit for PID output (reads from).
 > *FBMON - A monitor for the PID controller's feedback (writes to).
 > *OUT_EN - A boolean flag to indicate if the ouput is engaged (reads from).
 > *FB - The feedback output from the PID controller (writes to).
The script either populates them, or reads from them.

The following Python libraries are required:
 > simple_pid
 > ezca
 > warnings
 > argparse
 > time

Author: Nathan A. Holland.
Contact: nathan.holland@anu.edu.au
Date: 2018-11-05

Modified: 2018-11-19
Modified: 2018-12-18 - added a 1/16 s wait time, to try to sync with 16 Hz EPICS
"""
#-------------------------------------------------------------------------------
#Imports:
from simple_pid import PID;
from ezca import Ezca;
from warnings import warn;
import argparse;
import time;
#-------------------------------------------------------------------------------
#Script Configuration:
_pid_init_config = {"Kp" : 0.0, "Ki" : 0.0, "Kd" : 0.0, "setpoint" : 0.0,
	"sample_time" : 0.1, "output_limits" : (-10.0, 10.0)}
	#Initial configuration for the PID controller.
_version = "0.9.0"; #Version (major, minor, revision).
#-------------------------------------------------------------------------------
#Static, common:
__all__ = ["main"]; #You may be, mainly, interested in this.
#
_echo_in = "INMON"; #Echos the input to the MEDM screen.
_in_engage = "IN_EN"; #The input engage channel.
_exc = "EXC"; #The excitation channel.
_in2 = "IN2"; #The summed excitation, and input channel.
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
_echo_out = "FB"; #Echos the output to the MEDM screen.
#
_epics_write_kwargs = {"monitor" : False}; #Don't print the write to stdout.
#
_script_name = "CDS_PID.py";
_script_description = "A generic python PID filter, backend, for slow CDS " + \
	"PID filters."; #A description of the scripts function.
_pidfilt_help = "A string indicating the channel prefix to use. For " + \
	"example if the desired channels are A1:ISC-LASER_D_TEMP_* then " + \
	"the prefix to use is <A1:ISC-LASER_D_TEMP_>. The IFO indicator is " + \
	"omitted";
	#Help for the --PIDfilt argument.
_input_help = "A string indicating the input channel to use. " + \
	"For example if the desired input channel is " + \
	"A1:LSC-PDH_ERR_D_LF_NORM then the input channel is " + \
	"<A1:LSC-PDH_ERR_D_LF_NORM>. The IFO indicator is omitted.";
	#Help for the --inputs argument.
_output_help = "A string indicating the output channel to use. " + \
	"For example if the desired output channel is " + \
	"A1:ISC-LASER_D_XL_TEMP then the output channel is " + \
	"<A1:ISC-LASER_D_XL_TEMP>. The IFO indicator is omitted.";
	#Help for the --output argument.
#
_Ezca_kwargs = {"ifo" : ''}; #Don't pass ezca.Ezca an IFO identifier.
#-------------------------------------------------------------------------------
#Define the argument parser.
_parser = argparse.ArgumentParser(prog = _script_name,
	description = _script_description); #The argument parser.
_parser.add_argument("--version", action = "version", version = _version);
	#Add the version argument.
_parser.add_argument("--PIDfilt", help = _pidfilt_help, nargs = 1, type=str,
	required = True); #Add the PIDfilt argument.
_parser.add_argument("--input", help = _input_help, nargs = 1, type = str,
	required = True, default = None); #Add the input argument.
_parser.add_argument("--output", help = _output_help, nargs = 1, type = str,
	required = True, default = None); #Add the output argument.
#-------------------------------------------------------------------------------
#Main - the thing to do:
def main(channels_prefix, input_channel, output_channel):
	"Performs the main looping."
	#PID Initialisation:
	pid = PID(**_pid_init_config); #Create the PID controller.
	pid.auto_mode = True; #Output of the PID controller is engaged.
	#
	#EPICS Initialisation:
	epics_inout = Ezca(**_Ezca_kwargs);
		#Make a separate connection to the i/o.
	epics_inout.connect(input_channel); #Check connection to the input.
	epics_inout.connect(output_channel); #Check connection to the output.
	#
	epics_access = Ezca(prefix = channels_prefix, **_Ezca_kwargs);
		#Create the epics access object.
	epics_access.connect(_echo_in); #Check the input echoer.
	epics_access.connect(_in_engage);
		#Check the connection to input engage.
	epics_access.connect(_exc); #Check the connection to the excitation.
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
	epics_access.connect(_echo_out);
		#Check the connection to the output echoer.
	#If the channels aren't available then let ezca throw an error.
	#
	while True:
		#Loop forever.
		#Input -
		signal_in = epics_inout.read(input_channel); #Collect the input.
		epics_access.write(_echo_in, signal_in, **_epics_write_kwargs);
			#Write the input to INMON.
		excitation = epics_access.read(_exc); #Read any excitations.
		#Input switching -
		if epics_access.read(_in_engage):
			error = signal_in + excitation;
				#Calculate the error.
		else:
			error = excitation; #No filter input otherwise.
		#
		epics_access.write(_in2, error, **_epics_write_kwargs);
			#Write to channel IN2.
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
		if feedback is None:
			feedback = 0.0; #Feedback being None causes errors.
		else:
			pass; #Do nothing.
		#
		epics_access.write(_fbmon, feedback, **_epics_write_kwargs);
			#Write to the feedback monitor channel, no printing.
		#
		#Output switching -
		if epics_access.read(_out_engage):
			epics_inout.write(output_channel, feedback,
				**_epics_write_kwargs);
			epics_access.write(_echo_out, feedback,
				**_epics_write_kwargs);
				#Write the feedback, no printing.
		else:
			epics_inout.write(output_channel, 0.0,
				**_epics_write_kwargs);
			epics_access.write(_echo_out, 0.0,
				**_epics_write_kwargs);
				#Write nothing, no printing.
		
		# try to run at 16 Hz, like the general EPICS channels
		# wait for ~62 ms
		time.sleep(1.0/16.0);
		#
#
#-------------------------------------------------------------------------------
#Run:
if __name__ == "__main__":
	#Initialisation - pass arguments:
	_passed_args = _parser.parse_args(); #Pass the arguments.
	_args = vars(_passed_args); #Convert the namespace object to a dict.
	#Package arguments:
	_prefix = _args["PIDfilt"][0]; #Package prefix name.
	_in_chnl = _args["input"][0]; #User specified input channel.
	_fb_chnl = _args["output"][0]; #User specified.
	#
	#Call main:
	main(_prefix, _in_chnl, _fb_chnl); #Run the main part of the script
else:
	pass;
#
#-------------------------------------------------------------------------------
#END.
