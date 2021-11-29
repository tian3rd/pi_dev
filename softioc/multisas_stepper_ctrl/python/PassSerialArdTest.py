import serial;
import time;

## Pushing commands to the stepper motors
s1 = serial.Serial('/dev/ttyACM0',9600);
time.sleep(2)
s1.write('2.0.200.1.-200'.encode())

time.sleep(2)
## Checking if any switches are triggered by motion
SwitchFlag = s1.read(1);
SwitchFlag = format(int.from_bytes(SwitchFlag, byteorder='little'),'016b');
SwitchFlag = SwitchFlag[::-1];

for i in range(1,8):
    FirstDex = (2*(i-1));
    if bool(int(SwitchFlag[FirstDex])):
        print(''.join(str(j) for j in ['Motor ',(i-1),' Lower Limit Hit']))
    if bool(int(SwitchFlag[FirstDex+1])):
        print(''.join(str(j) for j in ['Motor ',(i-1),' Upper Limit Hit']))

## Checking Step Count Values
for i in range(1,5)
    StepVal = s1.read(2);
    print(''.join(str(j) for j in ['Motor ',(i-1),' Step Count: ', StepVal]))

## Terminating the serial connection to the Arduino
s1.close()
