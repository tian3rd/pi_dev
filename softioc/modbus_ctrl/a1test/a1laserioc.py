from simple_pid import PID
from ezca import Ezca

# Kp – 		The value for the proportional gain Kp
# Ki – 		The value for the integral gain Ki
# Kd – 		The value for the derivative gain Kd
# setpoint – 	The initial setpoint that the PID will try to achieve
#		sample_time – The time in seconds which the controller should wait 
#		before generating a new output value. The PID works best when it 
#		is constantly called (eg. during a loop), but with a sample time set 
#		so that the time difference between each update is (close to) 
#		constant. If set to None, the PID will compute a new output value 
#		every time it is called.
# output_limits – The initial output limits to use, given as an iterable with 2 elements, 
#		for example: (lower, upper). The output will never go below the 
#		lower limit or above the upper limit. Either of the limits can also 
#		be set to None to have no limit in that direction. Setting output 
#		limits also avoids integral windup, since the integral term will never 
#		be allowed to grow outside of the limits.
# auto_mode – 	Whether the controller should be enabled (in auto mode) or not (in manual mode)
# proportional_on_measurement – Whether the proportional term should be calculated on the 
#		input directly rather than on the error (which is the traditional way). 
#		Using proportional-on-measurement avoids overshoot for some types of systems.


pid.sample_time = 0.1
prefix = 'ISC-LASER'

while True:

	Kp = ezca.read('D_TEMP_KP')
	Ki = exca.read('D_TEMP_KI')
	Kd = ezca.read('D_TEMP_KD')

	setpoint = ezca.read('D_TEMP_SETPOINT')

	pid.output_limits = (-10, 10)

	if ezca['D_TEMP_EN'] == 1:
		pid.auto_mode = TRUE
	elif ezca['D_TEMP_EN'] == 0
		pid.auto_mode = FALSE
	else:
		# do nothing
	

	pid = PID(Kp, Ki, Kd, setpoint)
	ezca['D_TEMP_FB'] = pid(ezca['ISC-PHD_ERR_D_LF_NORM']


