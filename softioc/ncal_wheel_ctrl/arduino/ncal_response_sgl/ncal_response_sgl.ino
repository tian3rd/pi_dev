/* ncal_response
 *  
 *  simple command/response access via USB to Teensy
 *  
 *  This is to control the NCal ACS606 DC Servo Motor controller
 *  
 *  Bram Slagmolen
 *  bram.slagmolen@anu.edu.au
 *  
 *  6 January 2021
 */


/*
 * Declare libraries
*/
//#include <SoftwareSerial.h>                     // see https://www.pjrc.com/teensy/td_libs_SoftwareSerial.html
#include <FreqMeasure.h>                        // see https://www.pjrc.com/teensy/td_libs_FreqMeasure.html
#include <PID_v1.h>                             // see https://playground.arduino.cc/Code/PIDLibrary/

/* 
 *  Set constant
 *  
 */
const String SOFTWARE_VERSION = "2020-03-26";
const String SOFTWARE_ID = "ncal_response";

const byte BUFFER_LENGTH = 32;
const int COMMAND_LENGTH = 16;

const char END_MARKER = '\n';

const long USB_BAUD = 115200;

const int UNDEFINED = -1;

const int ENABLE = 1;                           // ENABLE Motor Driver
const int DISABLE = 0;                          // DISABLE Motor Driver

const float GEAR_RATIO = 2.22222;               // 40/18 Pulley with 40 Tooth on Wheel, and 18 Tooth on motor 
const float PULL_RATIO = 4000;                  // drive pulses per revolution

const float PULL_FREQUENCY_DEFAULT = 0;         // motor driver pull frequency
const float PULL_FREQUENCY_MIN = 0;
const float PULL_FREQUENCY_MAX = 45000;

const float ANGULAR_FREQUENCY_DEFAULT = 0;
const float ANGULAR_FREQUENCY_MIN = 0;
const float ANGULAR_FREQUENCY_MAX = 8;

const float ANGULAR_ACCELERATION_DEFAULT = 0.08;  // defaul acceleration 
const float ANGULAR_ACCELERATION_MIN = 0;
const float ANGULAR_ACCELERATION_MAX = 1;

const float KP_MIN = 0;
const float KP_MAX = 1000;
const float KI_MIN = 0;
const float KI_MAX = 1000;
const float KD_MIN = 0;
const float KD_MAX = 1000;

const int NUMBER_OF_HOLES_DEFAULT = 650;          // number of holes for the photo sensos
const int NUM_OF_HOLES_MIN = 1;
const int NUM_OF_HOLES_MAX = 1000;

const float PERIOD_1HZ = 1000;                    // 1 Hz update period, in milliseconds
const float PERIOD_16HZ = 62.5;                   // 16 Hz update period, in milliseconds
const float PERIOD_32HZ = 31.25;                  // 32 Hz update period, in milliseconds
const float SAMPLE_PERIOD = PERIOD_32HZ;

/*
 * Set Pins on the Teensy
 * 
 *    Pin 3 is used in the FreqMeasure function,
 *    which makes pin 4 unusable for ananolgWrite
 * 
 */
const int PULLPIN = 29;                   // FTM2 timer, linked to PWM pin 30
                                          // See PWM & Tone notes  
                                          // This pin is connected to the ACS606 -PULL pin of the driver
                                          
const int ENAPIN = 30;                    // Pin to control the Driver ENABLE state
                                          // HIGH (0) = enabled
                                          // LOW (1) = disabled

const int DIRPIN = 6;                     // Pin set to control the motor driver direction
                                          // we do not use this.

const int GATEPIN = 5;                    // pin to readout the photosensor, OMRON EE-SX672
                                          // This is a pick off from pin 3
                                        
const int LED = 24;                       // Teensy 3.x builtin LED pin -> moved to pin 24 and external LED

const int PPSLED = 13;                    // Teensy 3.5 led pin, lids up when processing command

/* 
 * Set variables
 *
 */
boolean newSerialData = false;            // Serial data semaphore
char receivedChars[BUFFER_LENGTH+1];      // received character string
char baseCmd[COMMAND_LENGTH+1];           // array for holding the command instruction
char arg1[COMMAND_LENGTH+1];              // array for holding the command argument

boolean val;
boolean semaphore_gate = LOW;
boolean semaphore_pid = LOW;
boolean semaphore_pps = LOW;

double freqRead = 0;
double sum = 0;
int count = 0;

boolean driver_state = DISABLE;           // State of Motor Dirver
boolean change_pull_freq = false;
boolean at_setpoint = false;
float delta = 0;                          // difference in PULL frequency

static uint32_t currentMillis;              // timer updated throughout.
static uint32_t freqmeasureMillis;          // used to count the measurement timing

static uint32_t oneppsMillis;               // used to count the 1 PPS timing
static uint32_t setpointMillis;             // also set in set_acc_pull_frequency

float angular_acceleration = ANGULAR_ACCELERATION_DEFAULT;

double angular_frequency_setpoint = ANGULAR_FREQUENCY_DEFAULT;         // Set point of the angular frequency
double angular_frequency_request = ANGULAR_FREQUENCY_DEFAULT;
double angular_frequency_pid = ANGULAR_FREQUENCY_DEFAULT;

double angular_frequency_meas = 0;              // the period of rotation of the wheel, Hz

double raw_frequency_meas = 0;

int number_of_holes = NUMBER_OF_HOLES_DEFAULT; // the number of holes around the circumference of the wheel

float pull_frequency = PULL_FREQUENCY_DEFAULT;              // set initial PULL pulse frequency, Hz
                                          // value of 4000 is  1 rotation per second of the motor axle
                                          // need to multiply by the gear ratio and request angular freq 
                                          // to get the actual pull frequency
                                          //    15 = ~0.01 Hz
                                          //  . 31 =  0.01 Hz
                                          //    62 =  0.02 Hz
                                          //   125 =  0.03 Hz
                                          //   250 =  0.06 Hz
                                          //   500 =  0.13 Hz
                                          //  1000 =  0.25 Hz
                                          //  2000 =  0.50 Hz
                                          //  4000 =  1.01 Hz
                                          //  8000 =  2.00 Hz
                                          // 10000 =  2.50 Hz
                                          // 16000 =  4.00 Hz
                                          // 20000 =  5.00 Hz
                                          // 30000 =  7.50 Hz
                                          // 32000 =  8.01 Hz
                                          // 40000 = 10.01 Hz
                                          // 45000 = 11.25 Hz

//Specify the links and initial tuning parameters
bool pid_state = DISABLE;
double Kp=1.0, Ki=0.2, Kd=0.01;
PID myPID(&raw_frequency_meas, &angular_frequency_pid, &angular_frequency_setpoint, Kp, Ki, Kd, REVERSE);
          
void setup() {
  
  pinMode(LED, OUTPUT);                   // 
  pinMode(PPSLED, OUTPUT);
  pinMode(GATEPIN, INPUT);                // Set the OMRON EE-SX672 (NPN), Light-ON, readout
  pinMode(PULLPIN, OUTPUT);               // Set Motor Driver PULL pin to output
  pinMode(DIRPIN, OUTPUT);                // Set Motor Driver DIR pin to output
  pinMode(ENAPIN, OUTPUT);                // Set Motor Driver ENA pin to output

  digitalWrite(ENAPIN, HIGH);             // disable driver
  digitalWrite(DIRPIN, LOW);              // Set Motor Driver DIR pin
                                          // need a transitor to sent signal to GND
                                          // Not required for NCal, we rotoating only in
                                          // a single direction

  digitalWrite(LED, LOW);                 // Set built-in led to OFF
  digitalWrite(PPSLED, LOW);              // Set built-in led to OFF

  set_pull_pin_pwm();                     // Set 20% PWM duty cycle pull frequency drive

  set_pull_frequency("set inital pull frequency");


  resetBuffer();                          // reset all communication buffers
  
  Serial.begin(USB_BAUD);
  while(!Serial);                         // Wait for USB Serial to connect
  
  Serial.print(F("cmd_response started: "));
  Serial.println(FreeMem());              // prints free memory, as a signature.

  myPID.SetSampleTime(PERIOD_16HZ);

  FreqMeasure.begin();                    // Set up the photo-gate Frequency Measurement function, on pin 3.

}


void loop() {
  
  recvWithStartEndMarkers();              // read command 
  commandProcess();                       // extract instruction and argument
  readGateSignal();                       // Read the photogate signal pick off


  // Update PID servo state, enable (automatic) and disable (manual)
  // the pid_state flag can be read out to check the state of the PID servo
  if ( (pid_state == ENABLE) && (semaphore_pid == LOW) ) {
    semaphore_pid = HIGH;
    myPID.SetMode(AUTOMATIC);
  } else if ( (pid_state == DISABLE) && (semaphore_pid == HIGH) ) {
    semaphore_pid = LOW;
    myPID.SetMode(MANUAL);
  }

  currentMillis = millis();

  // Change the setpoint, at the 16 Hz rate,
  // only possible when PID is disabled, and only when the motor driver is enabled
  if ( (change_pull_freq == HIGH) && (driver_state == ENABLE) && (pid_state == DISABLE) ) {
    
    digitalWrite(LED, HIGH);              // Visual LED indicator that we change setpoint
    
    if (currentMillis - setpointMillis >= PERIOD_16HZ) {
      
      if ((delta > 0) && (angular_frequency_request < angular_frequency_setpoint)) {
        angular_frequency_request += delta;
        set_pull_frequency("acc_pull_frequency >0");
        
      } else if ((delta < 0) && (angular_frequency_request > angular_frequency_setpoint)) {
        angular_frequency_request += delta;
        set_pull_frequency("acc_pull_frequency <0");
          
      } else if (((delta > 0) && (angular_frequency_request > angular_frequency_setpoint)) || ((delta < 0) && (angular_frequency_request < angular_frequency_setpoint))) {
        angular_frequency_request = angular_frequency_setpoint;
        set_pull_frequency("setpoint_pull_frequecy");
        change_pull_freq = LOW;
        digitalWrite(LED, LOW);
        
      }
      setpointMillis += PERIOD_16HZ;
    }
  }

  // Check if there is a signal on pin 3, 
  // to make the freq measurement available 
  if (FreqMeasure.available()) {
    
    // average several reading,
    freqRead = FreqMeasure.read();
    sum = sum + freqRead;

    count++;

    // Calculate the raw and angular frequency signals, and
    // Run the PID if enabled and not changing setpoint (=change_pull_freq)
    if (currentMillis - freqmeasureMillis >= SAMPLE_PERIOD) {
      raw_frequency_meas = FreqMeasure.countToFrequency(sum / count);
      angular_frequency_meas = raw_frequency_meas / number_of_holes;  // convert how many holes per second,
                                                                      // to angular fereq by scaling by the number of holes
      
      myPID.Compute();
      if ((pid_state == ENABLE) && (driver_state == ENABLE) && (change_pull_freq == LOW)) {
        //angular_frequency_request -= angular_frequency_pid;
        //set_pull_frequency("PID:");
      }     
       
      sum = 0;
      count = 0;
      freqmeasureMillis += SAMPLE_PERIOD;
    }
  } 

  // Calculate 1 Hz update rate, could be done using the 16 Hz signal instead
  if (currentMillis - oneppsMillis >= 1000 / 2) {
    if (semaphore_pps == LOW) {
      digitalWrite(PPSLED, HIGH);
      semaphore_pps = HIGH;
    } else if (semaphore_pps == HIGH) {
      digitalWrite(PPSLED, LOW);
      semaphore_pps = LOW;
    }
    oneppsMillis += PERIOD_1HZ / 2;
  } 
  
} /* loop */


/**
  * Finds the amount of free memory by calculating the difference
  * between the address of a new stack variable and the address of 
  * the end of the heap.
  * from https://forum.pjrc.com/threads/33443-How-to-display-free-ram?p=99128&viewfull=1#post99128
  */
uint32_t FreeMem(){ // for Teensy 3.0
    uint32_t stackTop;
    uint32_t heapTop;

    // current position of the stack.
    stackTop = (uint32_t) &stackTop;

    // current position of heap.
    void* hTop = malloc(1);
    heapTop = (uint32_t) hTop;
    free(hTop);

    // The difference is (approximately) the free, available ram.
    return stackTop - heapTop;
}

void set_pull_pin_pwm() {
  analogWrite(PULLPIN, 5);               // 20/255 PWM pulse witdth, min 0.85us pulse for ACS606
                                          // The pulse width is dependent on the frequency. The pulse width
                                          // can be minimum of 0.85us the ACS606 at whihc point it does not 
                                          // register the pulse.
                                          //
                                          // Although we can set any pulse width, I set the minimum pulse width.
                                          // This also sets the maximum angular velocity of the wheel, related
                                          // to the pull_frequency, as a safety factor. E.g. we can't go faster.
                                          //
                                          // We set the max pull_frequency to 45k (safety setting), and the 
                                          // pulse width to 0.85us, the minimum PWM pulse with would be
                                          // 0.85us * 2*255 * 45k  = 19.5 -> 20
                                          // factor of 2 is a scaling to set half the period to the pulse.
}

void readGateSignal() {
  // Read Photogate signal
  val = digitalRead(GATEPIN);
   
  //If photogate detects something, turn Teensy LED on
  if ((val == HIGH) && (semaphore_gate == 0)) {
    digitalWrite(LED, HIGH);
    semaphore_gate = 1;
  } else if ((val == LOW) && (semaphore_gate == 1))  {
    //Leave LED off otherwise
    digitalWrite(LED, LOW);
    semaphore_gate = 0;
  } 
}

void recvWithStartEndMarkers() {
    // Code obtained from https://forum.arduino.cc/index.php?topic=396450
    static byte ndx = 0;
    char endMarker = END_MARKER;
    char rc;
 
    while (Serial.available() > 0 && newSerialData == false) {
        rc = Serial.read();

        if (rc != endMarker) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= BUFFER_LENGTH) {
                ndx = BUFFER_LENGTH - 1;
            }
        }
        else {
            receivedChars[ndx] = '\0'; // terminate the string
            ndx = 0;
            newSerialData = true;
        }
     }
}

void commandProcess() {  
  char* cmd = 0;
  char temp[BUFFER_LENGTH+1];

  strcpy(temp, receivedChars);
  if (newSerialData == true) {
       
    cmd = strtok(temp, " ");
    strcpy(baseCmd, cmd);

    cmd = strtok(NULL, " ");
    if (cmd) {
      strcpy(arg1, cmd);

      cmd = strtok(NULL, " ");
      if (cmd) {
        Serial.print(F("ERROR_TOO_MANY_ARGUMENTS:"));
        Serial.println(temp);
        Serial.read();                 // empty serial input buffer
        }
      }

    if (strlen(baseCmd)) {
      if      (0 == strcmp(baseCmd, "?en"))       get_engage_driver(receivedChars);
      else if (0 == strcmp(baseCmd, "!en"))       set_engage_driver(receivedChars);   
      else if (0 == strcmp(baseCmd, "?pf"))       get_pull_frequency(receivedChars);
      else if (0 == strcmp(baseCmd, "!pf"))       set_pull_frequency(receivedChars);
      else if (0 == strcmp(baseCmd, "?sp"))       get_angular_frequency_setpoint(receivedChars);
      else if (0 == strcmp(baseCmd, "!sp"))       set_acc_pull_frequency(receivedChars);
      else if (0 == strcmp(baseCmd, "?as"))       get_at_setpoint(receivedChars);
      else if (0 == strcmp(baseCmd, "?if"))       get_raw_frequency_meas(receivedChars);
      else if (0 == strcmp(baseCmd, "?af"))       get_angular_frequency_meas(receivedChars);
      else if (0 == strcmp(baseCmd, "?aa"))       get_angular_acceleration(receivedChars);
      else if (0 == strcmp(baseCmd, "!aa"))       set_angular_acceleration(receivedChars);
      else if (0 == strcmp(baseCmd, "?ep"))       get_engage_pid(receivedChars);
      else if (0 == strcmp(baseCmd, "!ep"))       set_engage_pid(receivedChars);
      else if (0 == strcmp(baseCmd, "?kp"))       get_kp(receivedChars);
      else if (0 == strcmp(baseCmd, "!kp"))       set_kp(receivedChars);
      else if (0 == strcmp(baseCmd, "?ki"))       get_ki(receivedChars);
      else if (0 == strcmp(baseCmd, "!ki"))       set_ki(receivedChars);
      else if (0 == strcmp(baseCmd, "?kd"))       get_kd(receivedChars);
      else if (0 == strcmp(baseCmd, "!kd"))       set_kd(receivedChars);     
      else if (0 == strcmp(baseCmd, "?pd"))       get_pid_direction(receivedChars);     
      else if (0 == strcmp(baseCmd, "!pd"))       set_pid_direction(receivedChars);     
      else if (0 == strcmp(baseCmd, "?pid"))      get_angular_frequency_pid(receivedChars);     
      else if (0 == strcmp(baseCmd, "?pps"))      get_one_pps(receivedChars);     
      else if (0 == strcmp(baseCmd, "!h"))        set_number_of_holes(receivedChars);
      else if (0 == strcmp(baseCmd, "?h"))        get_number_of_holes(receivedChars);
      else if (0 == strcmp(baseCmd, "?v"))        get_software_version(receivedChars);
      else if (0 == strcmp(baseCmd, "?id"))       get_software_id(receivedChars);
      else {
        Serial.print(F("ERROR_UNKNOWN_COMMAND:"));
        finaliseError(receivedChars);
      }
    } /* if strlen(baseCmd) */
 
    newSerialData = false;
  } // if newSerialData
}

void finaliseError(char *in) {
  Serial.println(in);
  resetBuffer();
}

void resetBuffer() {
  receivedChars[0] = '\0';
  newSerialData = false;
  baseCmd[0] = '\0';
  arg1[0] = '\0';
}

void get_engage_driver(char* in) {
  boolean tmp = digitalRead(ENAPIN);
  
  if ( ((tmp != DISABLE) == (tmp != ENABLE))) {
    Serial.print(F("ERROR_GET_ENGAGE_DRIVER:"));
    finaliseError(in);  
    } else {
      Serial.println(!tmp);
    }
}

void set_engage_driver(char* in) {
  int tmp = atoi(arg1);
  
  if ( ((tmp != DISABLE) == (tmp != ENABLE))) {
    Serial.print(F("ERROR_SET_ENGAGE_DRIVER:"));
    finaliseError(in);
    
  } else if (tmp == ENABLE)  {
    digitalWrite(ENAPIN, LOW);
    driver_state = ENABLE;
    Serial.println(F("Ok"));
    
  } else if (tmp == DISABLE) {
    digitalWrite(ENAPIN, HIGH);
    driver_state = DISABLE;
    pid_state = DISABLE;
    angular_frequency_setpoint = 0;
    angular_frequency_request = 0;
    set_pull_frequency("DISABLE:");
    Serial.println(F("Ok"));
  }
}

void get_engage_pid(char* in) {
  boolean tmp = myPID.GetMode();                    // return: AUTOAMTIC = 1
                                                    // return: MANUAL = 0
  
  if ( ((tmp != DISABLE) == (tmp != ENABLE))) {
    Serial.print(F("ERROR_GET_ENGAGE_PID:"));
    finaliseError(in);
    
    } else {
      Serial.println(tmp);
    }
}

void set_engage_pid(char* in) {
  int tmp = atoi(arg1);
  
  if ( ((tmp != DISABLE) == (tmp != ENABLE)) ) {
    Serial.print(F("ERROR_SET_ENABLE_PID:"));
    finaliseError(in);
    
  } else if ((tmp == ENABLE) && (driver_state == ENABLE)) {
    pid_state = ENABLE;
    Serial.println(F("Ok"));
    
  } else if (tmp == DISABLE) {
    pid_state = DISABLE;
    Serial.println(F("Ok"));
  }
}

void get_pull_frequency(char* in) {
  Serial.println(pull_frequency);  
}

void set_pull_frequency(char* in) {
  /*
   * Here is were we set the actual motor pull frequency
   */
  float tmp = angular_frequency_request * GEAR_RATIO * PULL_RATIO;
  
  if (tmp < PULL_FREQUENCY_MIN || tmp > PULL_FREQUENCY_MAX) {
    Serial.print(F("ERROR_PULL_FREQUENCY_RANGE:"));
    finaliseError(in);
  } else {
    pull_frequency = tmp;
    analogWriteFrequency(PULLPIN, pull_frequency);  // set PWM pulse frequency, Hz
                                                    // see https://www.pjrc.com/teensy/td_pulse.html
  }
  
}

void set_acc_pull_frequency(char* in) {
  float tmp = atof(arg1);

  if (tmp < ANGULAR_FREQUENCY_MIN || tmp > ANGULAR_FREQUENCY_MAX) {
    Serial.print(F("ERROR_ACC_PULL_FREQUENCY_RANGE:"));
    finaliseError(in);
    
  } else if (angular_frequency_setpoint != tmp) {
    delta = angular_acceleration * PERIOD_16HZ / 1000;

    if (tmp < angular_frequency_setpoint) {
      delta = -1 * delta; 
    }

    angular_frequency_setpoint = tmp;

    pid_state = DISABLE;
    change_pull_freq = HIGH;
    Serial.println(F("Ok"));
    
    setpointMillis = millis();   
  }
 
}

void get_angular_frequency_setpoint(char* in) {
  Serial.println(angular_frequency_setpoint);
}

void get_at_setpoint(char* in) {
  if (change_pull_freq == LOW) {
    Serial.println(ENABLE);
  }
  if (change_pull_freq == HIGH) {
    Serial.println(DISABLE);
  }
}

void get_one_pps(char* in) {
  Serial.println(semaphore_pps);
}

void get_raw_frequency_meas(char* in) {
  Serial.println(raw_frequency_meas);
}

void get_angular_frequency_meas(char* in) {
  Serial.println(angular_frequency_meas);
}

void get_angular_acceleration(char* in) {
  Serial.println(angular_acceleration);
}

void set_angular_acceleration(char* in) {
  float tmp = atof(arg1);
  
  if (tmp < ANGULAR_ACCELERATION_MIN || tmp > ANGULAR_ACCELERATION_MAX) {
    Serial.print(F("ERROR_ANGULAR_ACCELERATION_RANGE:"));
    finaliseError(in);
  } else {
    angular_acceleration = tmp;
    Serial.println(F("Ok"));
  }
}

void get_kp(char* in) {
  Serial.println(myPID.GetKp());
}

void set_kp(char* in) {
  int tmp = atof(arg1);
  
  if (tmp < KP_MIN || tmp > KP_MAX) {
    Serial.print(F("ERROR_KP:"));
    finaliseError(in);
  } else {
    Kp = tmp;
    myPID.SetTunings(Kp, Ki, Kd);
    Serial.println(F("Ok"));
  }  
}

void get_ki(char* in) {
  Serial.println(myPID.GetKi());
}

void set_ki(char* in) {
  int tmp = atof(arg1);
  
  if (tmp < KI_MIN || tmp > KI_MAX) {
    Serial.print(F("ERROR_KI:"));
    finaliseError(in);
  } else {
    Ki = tmp;
    myPID.SetTunings(Kp, Ki, Kd);
    Serial.println(F("Ok"));
  }  
}

void get_kd(char* in) {
  Serial.println(myPID.GetKd());
}

void set_kd(char* in) {
  int tmp = atof(arg1);
  
  if (tmp < KD_MIN || tmp > KD_MAX) {
    Serial.print(F("ERROR_KD:"));
    finaliseError(in);
  } else {
    Kd = tmp;
    myPID.SetTunings(Kp, Ki, Kd);
    Serial.println(F("Ok"));
  }  
}

void get_pid_direction(char* in) {
  int tmp = myPID.GetDirection();
  Serial.println(tmp);
}

void set_pid_direction(char* in) {
  int tmp = atoi(arg1);

  if ( ((tmp != 1) == (tmp != 0))) {
    Serial.print(F("ERROR_PID_DIRECTION:"));
    finaliseError(in);
    
  } else if (tmp == 0) {
    myPID.SetControllerDirection(DIRECT);
    Serial.println(F("Ok"));
    
  } else if (tmp == 1) {
    myPID.SetControllerDirection(REVERSE);
    Serial.println(F("Ok"));
  }
}

void get_angular_frequency_pid(char* in) {
  Serial.println(angular_frequency_pid);
}

void get_number_of_holes(char* in) {
  Serial.println(number_of_holes);
}

void set_number_of_holes(char* in) {
  int tmp = atoi(arg1);
  
  if (tmp < NUM_OF_HOLES_MIN || tmp > NUM_OF_HOLES_MAX) {
    Serial.print(F("ERROR_NUMBER_OF_HOLES_RANGE:"));
    finaliseError(in);
  } else {
    number_of_holes = tmp;
    Serial.println(F("Ok"));
  }  
}

void get_software_version(char* in) {
  Serial.println(SOFTWARE_VERSION);
}

void get_software_id(char* in) {
  Serial.println(SOFTWARE_ID);
}
