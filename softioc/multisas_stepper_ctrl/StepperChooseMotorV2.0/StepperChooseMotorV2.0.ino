// Script runs stepper motor With limit switches
// This script is designed for usage with the Remote Stepper Motor Controller unit
// Switches need 10k ohm pulldown resistors
// Serial formating is 'NumMotors.Motor1Num.Motor1Steps.Motor2Num.Motor2Steps. ect. ect.)
int StepsPerRev = 200; // just a default call (not used)
int SpeedMotors = 10; // Higher = Slower. Full period is double this number in miliseconds (20 seems stable)

// Note: Don't plug in digital pin 0, 1 or 13. They are used for other functions.
byte LEDpin = 13; // Used to indicate the drive command is running
int LimitVals = 0;

// Motor Pins
byte NumAttachedMotors = 5;
byte PULp[] = {2, 5, 8, 22, 25};
byte DIRp[] = {3, 6, 9, 23, 26};
byte ENAp[] = {4, 7, 10, 24, 27};

// SwitchingPins
byte LLim[] = {41, 43, 45, 47, 48};
byte ULim[] = {40, 42, 44, 46, 49};

// Motor Enable Pins
byte MPen = 52;
byte MPind = 53;

// Stepper Motor Step Counter Reset Point
long StepResetCnt[] = {2147483647, 2147483647, 2147483647, 2147483647, 2147483647};
long StepCnt[5];

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // Setting up the motor digital I/O pins
  for (int i = 0; i < (&PULp)[1] - PULp; i++) {
    pinMode( PULp[i], OUTPUT);
  }
  for (int i = 0; i < (&DIRp)[1] - DIRp; i++) {
    pinMode( DIRp[i], OUTPUT);
  }
  for (int i = 0; i < (&ENAp)[1] - ENAp; i++) {
    pinMode( ENAp[i], OUTPUT);
  }

  // Setting up the Limit Switch digital I/O pins
  for (int i = 0; i < (&ULim)[1] - ULim; i++) {
    pinMode( ULim[i], INPUT); // Uses automatic pull-down resistor
  }
  for (int i = 0; i < (&LLim)[1] - LLim; i++) {
    pinMode( LLim[i], INPUT); // Uses automatic pull-down resistor
  }

  // Setting up the indicator light
  pinMode(LEDpin, OUTPUT);
  digitalWrite(LEDpin, LOW);

  // Enabling the Motor Power Enable Switches
  pinMode(MPen, OUTPUT);
  digitalWrite(MPen, LOW);
  pinMode(MPind, INPUT);

  // Step Counter Setup
  for (int i = 0; i < (&StepResetCnt)[1] - StepResetCnt; i++) {
    StepCnt[i] = StepResetCnt[i];
  }
}

void loop() {
  if (Serial.available() > 0)
  {
    int NumMotors = Serial.parseInt(); // Determine number of motors to drive

    if (NumMotors == 6) {
      int CmdNum = Serial.parseInt(); // If no motors are to be driven a system command is being requested

      // --- System Command (0.0): All Off ---
      if (CmdNum == 0) {
        // Turning Everything off again
        for (int i = 0; i < (&PULp)[1] - PULp; i++) {
          digitalWrite(ENAp[i], HIGH); // Turn motors off
          digitalWrite(DIRp[i], LOW); // Turn direction line off
        }
        digitalWrite(LEDpin, LOW); // On board light shows no longer driving

        // Passing error flags back to python
        LimitVals = 0;
        Serial.write(LimitVals);

        // Turn off Motors
        digitalWrite(MPen, LOW);

        // Pass Back Step Counters
        for (int i = 0; i < 5; i++) {
          byte PassOut[4];
          PassOut[0] = (byte) ((StepCnt[i] & 0xFF000000) >> 24 );
          PassOut[1] = (byte) ((StepCnt[i] & 0x00FF0000) >> 16 );
          PassOut[2] = (byte) ((StepCnt[i] & 0x0000FF00) >> 8  );
          PassOut[3] = (byte) ((StepCnt[i] & 0X000000FF)       );
          Serial.write(PassOut[0]);
          Serial.write(PassOut[1]);
          Serial.write(PassOut[2]);
          Serial.write(PassOut[3]);
        }
      }
      // --- System Command (0.1): Stepper Drivers On ---
      else if (CmdNum == 1) {
        digitalWrite(MPen, HIGH);
        Serial.write(LimitVals);

        // Pass Back Step Counters
        for (int i = 0; i < 5; i++) {
          byte PassOut[4];
          PassOut[0] = (byte) ((StepCnt[i] & 0xFF000000) >> 24 );
          PassOut[1] = (byte) ((StepCnt[i] & 0x00FF0000) >> 16 );
          PassOut[2] = (byte) ((StepCnt[i] & 0x0000FF00) >> 8  );
          PassOut[3] = (byte) ((StepCnt[i] & 0X000000FF)       );
          Serial.write(PassOut[0]);
          Serial.write(PassOut[1]);
          Serial.write(PassOut[2]);
          Serial.write(PassOut[3]);
        }
      }
      // --- System Command (0.2): Quote Status ---
      else if (CmdNum == 2) {
        LimitVals = 0;
        // ------- Limit Switches -------
        for (int j = 0; j < (&LLim)[1] - LLim; j++) {
          // Check each switch
          bool LowLimHit = (digitalRead(LLim[j]) == LOW);
          bool UpLimHit = (digitalRead(ULim[j]) == LOW);

          // Raising the associated Flag
            if (LowLimHit) {
              bitSet(LimitVals, (2 * j));
            }
            if (UpLimHit) {
              bitSet(LimitVals, (2 * j) + 1);
            }
        }
        Serial.write(LimitVals);

        // Pass Back Step Counters
        for (int i = 0; i < 5; i++) {
          byte PassOut[4];
          PassOut[0] = (byte) ((StepCnt[i] & 0xFF000000) >> 24 );
          PassOut[1] = (byte) ((StepCnt[i] & 0x00FF0000) >> 16 );
          PassOut[2] = (byte) ((StepCnt[i] & 0x0000FF00) >> 8  );
          PassOut[3] = (byte) ((StepCnt[i] & 0X000000FF)       );
          Serial.write(PassOut[0]);
          Serial.write(PassOut[1]);
          Serial.write(PassOut[2]);
          Serial.write(PassOut[3]);
        }
      }
      // --- System Command (0.3): Reset Steppers ---
      else if (CmdNum == 3) {
        // Reset counters
        for (int i = 0; i < (&StepResetCnt)[1] - StepResetCnt; i++) {
          StepCnt[i] = StepResetCnt[i];
        }

        Serial.write(LimitVals);

        // Pass Back Step Counters
        for (int i = 0; i < 5; i++) {
          byte PassOut[4];
          PassOut[0] = (byte) ((StepCnt[i] & 0xFF000000) >> 24 );
          PassOut[1] = (byte) ((StepCnt[i] & 0x00FF0000) >> 16 );
          PassOut[2] = (byte) ((StepCnt[i] & 0x0000FF00) >> 8  );
          PassOut[3] = (byte) ((StepCnt[i] & 0X000000FF)       );
          Serial.write(PassOut[0]);
          Serial.write(PassOut[1]);
          Serial.write(PassOut[2]);
          Serial.write(PassOut[3]);
        }
      }
    }
    else if ((NumMotors < NumAttachedMotors) & (NumMotors > 0)) {
      // ------- Determining the motors to drive and for how long -------
      int Motors2Use[NumMotors];
      int StepsPerRev[NumMotors];
      int MaxStepsPerRev = 0;
      for (int j = 0; j < abs(NumMotors); j++) {
        Motors2Use[j] = Serial.parseInt(); // Specifying the motor to drive
        StepsPerRev[j] = Serial.parseInt(); // Determine number of steps to drive the motor

        if (abs(StepsPerRev[j]) > MaxStepsPerRev) {
          MaxStepsPerRev = abs(StepsPerRev[j]); // Motors will be active for largest drive time passed
        }

        // Setting the motor directions
        if (StepsPerRev[j] > 0) {
          digitalWrite(DIRp[Motors2Use[j]], HIGH); // Forwards
        }
        else {
          digitalWrite(DIRp[Motors2Use[j]], LOW); // Backwards
        }
      }

      // ------- Turning on Stepper Drivers  -------
      digitalWrite(MPen, HIGH); // Turns on power to the stepper modules

      // ------- Beginning the Drive Process -------
      digitalWrite(LEDpin, HIGH); // On board light shows start of driving
      // Turning on all the required motors
      for (int i = 0; i < (&Motors2Use)[1] - Motors2Use; i++) {
        digitalWrite(ENAp[Motors2Use[i]], LOW); // Enable drive (Don't hand rotate motor)
      }

      // Stepping the motors
      for (int i = 0; i < MaxStepsPerRev; i++)
      {
        // Manually running the steps
        for (int j = 0; j < (&Motors2Use)[1] - Motors2Use; j++) {
          if (i < abs(StepsPerRev[j])) {
            digitalWrite(PULp[Motors2Use[j]], HIGH); // Pull to next step
          }
        }
        delay(SpeedMotors);
        for (int j = 0; j < (&Motors2Use)[1] - Motors2Use; j++) {
          if (i < abs(StepsPerRev[j])) {
            digitalWrite(PULp[Motors2Use[j]], LOW); // Reset at step
          }
        }
        delay(SpeedMotors);
        for (int j = 0; j < (&Motors2Use)[1] - Motors2Use; j++) { // Recording the motion
          if (i < abs(StepsPerRev[j])) {
            bool DirectionFlag = (digitalRead(DIRp[Motors2Use[j]]) == HIGH);
            if (DirectionFlag) {
              StepCnt[Motors2Use[j]] = ++StepCnt[Motors2Use[j]]; // Increase Step Count by 1
            }
            else {
              StepCnt[Motors2Use[j]] = --StepCnt[Motors2Use[j]]; // Decrease Step Count by 1
            }
          }
        }

        // ------- Limit Switches -------
        for (int j = 0; j < (&Motors2Use)[1] - Motors2Use; j++) {
          // Check each switch
          bool LowLimHit = bool (digitalRead(LLim[Motors2Use[j]]) == LOW);
          bool UpLimHit = bool (digitalRead(ULim[Motors2Use[j]]) == LOW);
          
          if ((LowLimHit || UpLimHit) && (i < abs(StepsPerRev[j]))) {
            delay(200);
          if ((LowLimHit || UpLimHit) && (i < abs(StepsPerRev[j]))) {
            digitalWrite(DIRp[Motors2Use[j]], !digitalRead(DIRp[Motors2Use[j]])); // Turn the motor around
            StepsPerRev[j] = 0; // No more motion from this command

            digitalWrite(PULp[Motors2Use[j]], HIGH); // Step backwards one step
            delay(SpeedMotors);
            digitalWrite(PULp[Motors2Use[j]], LOW);
            delay(SpeedMotors);

            // Raising the associated Flag
            if (LowLimHit) {
              bitSet(LimitVals, (2 * j));
            }
            if (UpLimHit) {
              bitSet(LimitVals, (2 * j) + 1);
            }
          }
          }
        }
      }


      // Turning Everything off again
      for (int i = 0; i < (&Motors2Use)[1] - Motors2Use; i++) {
        digitalWrite(ENAp[Motors2Use[i]], HIGH); // Turn motors off
        digitalWrite(DIRp[Motors2Use[i]], LOW); // Turn direction line off
      }
      digitalWrite(LEDpin, LOW); // On board light shows no longer driving

      // Passing error flags back to python
      Serial.write(LimitVals);

      // Pass Back Step Counters
      for (int i = 0; i < 5; i++) {
        byte PassOut[4];
        PassOut[0] = (byte) ((StepCnt[i] & 0xFF000000) >> 24 );
        PassOut[1] = (byte) ((StepCnt[i] & 0x00FF0000) >> 16 );
        PassOut[2] = (byte) ((StepCnt[i] & 0x0000FF00) >> 8  );
        PassOut[3] = (byte) ((StepCnt[i] & 0X000000FF)       );
        Serial.write(PassOut[0]);
        Serial.write(PassOut[1]);
        Serial.write(PassOut[2]);
        Serial.write(PassOut[3]);
      }
    }
  }
}
