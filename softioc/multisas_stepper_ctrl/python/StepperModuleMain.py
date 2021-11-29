import serial;
import time;
import termios;

## Pushing commands to the stepper motors
path = '/dev/ttyACM0'
with open(path) as f:
    attrs = termios.tcgetattr(f)
    attrs[2] = attrs[2] & ~termios.HUPCL
    termios.tcsetattr(f,termios.TCSAFLUSH,attrs)
s1 = serial.Serial(path,9600);
time.sleep(2)

# 6.0 -> All stepper controllers off.
#s1.write('6.0'.encode())

# 6.1 -> Stepper Controllers on.
s1.write('6.1'.encode())

# 6.2 -> Quote current step totals and switch status.
# s1.write('6.2'.encode())

# 6.3 -> Reset current step totals to 0.
#s1.write('6.3'.encode())

# Run the Harmonic DC Yaw Motor (motor number 4) 10 steps up(?)
# Positive number = clockwise while looking down from the top
#s1.write('1.4.-500'.encode())

# Run the Vertical Motor (motor number 3) 10 steps up(?)
# negative blade badse goes down
#s1.write('1.3.150'.encode())


## -- Commands -- ##
# X.Y0.Z0 -> Drive X motors. Drive motor Y0, Z0 steps.
# Maybe extend by adding more .Yn.Zn to the end of each other motor.
# eg. 1.0.400 drives motor 0 400 steps in the positive direction (Matches LVDT)

# 6.0 -> All stepper controllers off.
# 6.1 -> Stepper Controllers on.
# 6.2 -> Quote current step totals and switch status.
# 6.3 -> Reset current step totals to 0.

## Notes ##
## Roughly found that 200 steps of the harmonic drive is
# ~1 spacing of holes on the mid ring.
## Roughly ~1000 steps is the space between holes on
# the horizontal stepper frame.

time.sleep(2)
## Checking if any switches are triggered by motion
SwitchFlag = s1.read(1);
SwitchFlag = format(int.from_bytes(SwitchFlag, byteorder='little'),'016b');
SwitchFlag = SwitchFlag[::-1];

for i in range(1,8):
    FirstDex = (2*(i-1));
    if bool(int(SwitchFlag[FirstDex])):
        print(''.join(str(j) for j in ['Motor ',(i),' Lower Limit Hit']))
    if bool(int(SwitchFlag[FirstDex+1])):
        print(''.join(str(j) for j in ['Motor ',(i),' Upper Limit Hit']))

## Checking Step Count Values
for i in range(1,6):
    StepVal = s1.read(4);
    StepVal = int.from_bytes(StepVal, byteorder='big') - 2147483647;
    print(''.join(str(j) for j in ['Motor ',(i),' Step Count: ', StepVal]))

## Terminating the serial connection to the Arduino
s1.close()
