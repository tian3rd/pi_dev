/* ncal_response
 *  
 *  advance response access via USB to Teensy
 *  
 *  This is to control the NCal ACS606 DC Servo Motor controller with dual serial prts (_ds)
 *  
 *  This used a dual serial communication
 *  - default USB serial for the slow control parameters
 *  - serial 1 (second port) for the high bandwidth data comm
 *  
 *  Bram Slagmolen
 *  bram.slagmolen@anu.edu.au
 *  
 *  28 Mar 2021
 */


/*
 * Declare libraries
*/
//#include <FreqMeasure.h>                        // see https://www.pjrc.com/teensy/td_libs_FreqMeasure.html, using pin 3
#include <FreqMeasureMulti.h>                   // see https://github.com/PaulStoffregen/FreqMeasureMulti, using pin 9 and 10
//#include <PID_v1.h>                           // see https://playground.arduino.cc/Code/PIDLibrary/
//#include <TimeLib.h>
//#include <TimeAlarms.h>

// set this to the hardware serial port you wish to use
#define USBSERIAL Serial                        // Used for general control and interface
#define HWSERIAL Serial1                        // Used for Real-Time data comms,
                                                // Rx pin 0 (T3.5) -> Tx pin 8 (RPI),
                                                // Tx pin 1 (T3.5) -> Rx pin 10 (RPI)

#define TIME_HEADER  "T"                        // Header tag for serial time sync message
#define TIME_REQUEST  7                         // ASCII bell character requests a time sync message 

/* 
 *  Set constant
 *  
 */
const String SOFTWARE_VERSION = "2020-04-26";
const String SOFTWARE_ID = "ncal_response_tst";

const byte BUFFER_LENGTH = 32;
const int COMMAND_LENGTH = 16;

const char END_MARKER = '\n';

const long USB_BAUD = 115200;
const long DATA_BAUD = 115200;

//const int UNDEFINED = -1;

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

//const double KP_DEFAULT = 1.0;
//const double KP_MIN = 0;
//const double KP_MAX = 1000;

//const double KI_DEFAULT = 0.2;
//const double KI_MIN = 0;
//const double KI_MAX = 1000;

//const double KD_DEFAULT = 0.01;
//const double KD_MIN = 0;
//const double KD_MAX = 1000;

const int NUMBER_OF_HOLES_DEFAULT = 650;          // number of holes for the photo sensos
const int NUM_OF_HOLES_MIN = 1;
const int NUM_OF_HOLES_MAX = 1000;

const uint32_t PERIOD_1HZ = 1000UL;                  // 1 Hz update period, in milliseconds
const uint32_t PERIOD_16HZ = 62UL;                   // 16 Hz update period, in milliseconds
const uint32_t PERIOD_32HZ = 31UL;                   // 32 Hz update period, in milliseconds
const uint32_t SAMPLE_PERIOD = PERIOD_32HZ;

FreqMeasureMulti freq1;
FreqMeasureMulti freq2;

/*
 * Set Pins on the Teensy
 *
 */
// const int FREQPIN = 3;                 //  Pin 3 is used in the FreqMeasure function,
                                          //  which makes pin 4 unusable for ananolgWrite
 
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
                                        
//const int LED = 24;                       // Teensy 3.x builtin LED pin -> moved to pin 24 and external LED

const int PPSLED = 13;                    // Teensy 3.5 led pin, lids up when processing command

/* 
 * Set variables
 *
 */
bool newSerialData = false;               // Serial data semaphore
char receivedChars[BUFFER_LENGTH+1];      // received character string
char baseCmd[COMMAND_LENGTH+1];           // array for holding the command instruction
char arg1[COMMAND_LENGTH+1];              // array for holding the command argument

// bool val;
// bool semaphore_gate = LOW;
bool semaphore_pid = LOW;
bool semaphore_pps = LOW;
static int last_pin_state = LOW;

//double freqRead = 0;
double sum = 0;
double sum1 = 0;
double sum2 = 0;
int count = 0;
int count1 = 0;
int count2 = 0;

int gateCounter = 0;
float delta = 0;                          // difference in PULL frequency

bool driver_state = DISABLE;              // State of Motor Dirver
bool change_pull_freq = false;
bool at_setpoint = false;

static uint32_t currentMillis;              // timer updated throughout.
static uint32_t freqmeasureMillis;          // used to count the measurement timing
//static uint32_t currentTime;                // current time (in seconds) since 1 Jan 1970

static uint32_t oneppsMillis;               // used to count the 1 PPS timing
//elapsedMillis oneSecond;
//unsigned long setpointMillis;             // also set in set_acc_pull_frequency
//static uint32_t prevTime;                   // previous time in seconds

float angular_acceleration = ANGULAR_ACCELERATION_DEFAULT;

double angular_frequency_setpoint = ANGULAR_FREQUENCY_DEFAULT;         // Set point of the angular frequency
double angular_frequency_request = ANGULAR_FREQUENCY_DEFAULT;
double angular_frequency_pid = ANGULAR_FREQUENCY_DEFAULT;

double angular_frequency_meas = 0;              // the period of rotation of the wheel, Hz
double angular_frequency_meas2 = 0;              // the period of rotation of the wheel, Hz

double raw_frequency_meas = 0;
double raw_frequency_meas1 = 0;
double raw_frequency_meas2 = 0;

int number_of_holes = NUMBER_OF_HOLES_DEFAULT; // the number of holes around the circumference of the wheel

float pull_frequency = PULL_FREQUENCY_DEFAULT;              // set initial PULL pulse frequency, Hz
                                          // value of 4000 is  1 rotation per second of the motor axle
                                          // need to multiply by the gear ratio and request angular freq 
                                          // to get the actual pull frequency
                                          //    15 = ~0.01 Hz
                                          //    31 =  0.01 Hz
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

bool pid_state = DISABLE;
//double Kp = KP_DEFAULT;                   // Set proportional gain to DEFAULT
//double Ki = KI_DEFAULT;                   // Set integral gain to DEFAULT
//double Kd = KD_DEFAULT;                   // Set Diffiretial gain to DEFAULT

//PID myPID(&raw_frequency_meas, &angular_frequency_pid, &angular_frequency_setpoint, Kp, Ki, Kd, REVERSE);


void setup() {
  
  //pinMode(FREQPIN, INPUT);              // No need for declariation as this is done with FreqMeasure
  pinMode(GATEPIN, INPUT);                // Set the OMRON EE-SX672 (NPN), Light-ON, readout
  
  //pinMode(LED, OUTPUT);                   // 
  pinMode(PPSLED, OUTPUT);
    
  pinMode(PULLPIN, OUTPUT);               // Set Motor Driver PULL pin to output
  pinMode(DIRPIN, OUTPUT);                // Set Motor Driver DIR pin to output
  pinMode(ENAPIN, OUTPUT);                // Set Motor Driver ENA pin to output

  digitalWrite(ENAPIN, HIGH);             // disable driver
  digitalWrite(DIRPIN, LOW);              // Set Motor Driver DIR pin
                                          // need a transitor to sent signal to GND
                                          // Not required for NCal, we rotoating only in
                                          // a single direction

  //digitalWrite(LED, LOW);                 // Set built-in led to OFF
  digitalWrite(PPSLED, LOW);              // Set built-in led to OFF

  set_pull_pin_pwm();                     // Set 20% PWM duty cycle pull frequency drive

  // myPID.SetSampleTime(SAMPLE_PERIOD);
  
  USBSERIAL.begin(USB_BAUD);              // establish USB command communication
  HWSERIAL.begin(DATA_BAUD);              // establish Serial parameter communication

  resetBuffer();                          // reset all communication buffers

  USBSERIAL.print(F("cmd_response started: "));
  USBSERIAL.println(FreeMem());              // prints free memory, as a signature.

  //FreqMeasure.begin();                    // Set up the photo-gate Frequency Measurement function, on pin 3.
  freq1.begin(9);
  freq2.begin(10);

  delay(2000);                            // Wait 2 s to let the Servo Driver settled before writing pull freq

  //angular_frequency_request = 0;        // already DEFAULT value
  set_pull_frequency("acc_pull_frequency = 0");
  
  // set driver_state = ENABLE;
  strcpy(arg1, "0");
  set_engage_driver("disable driver");

  // set angular_frequency_setpoint = 0;
  strcpy(arg1, "0");
  set_acc_pull_frequency("set setpoint");
  
} /* Setup */


void loop() {

  recvWithStartEndMarkers();              // read command 
  commandProcess();                       // extract instruction and argument

  // Check if there is a signal on pin 3, 
  // to make the freq measurement available 
  //if (FreqMeasure.available()) {
  //  // average several reading,
  //  sum = sum + FreqMeasure.read();
  //  count++;
  //} 
  if (freq1.available()) {
    // average several reading,
    sum1 = sum1 + freq1.read();
    count1++;
  }
  if (freq2.available()) {
    // average several reading,
    sum2 = sum2 + freq2.read();
    count2++;
  }

  // count++;
  gateCounter++;
  // gateCount();
  
  currentMillis = millis();

  if (currentMillis - freqmeasureMillis >= SAMPLE_PERIOD) {
    //raw_frequency_meas = FreqMeasure.countToFrequency(sum / count); //gateCounter;
    
    raw_frequency_meas = freq1.countToFrequency(sum1 / count1);
    raw_frequency_meas2 = freq2.countToFrequency(sum2 / count2);
    
    angular_frequency_pid = gateCounter;
    
    angular_frequency_meas = raw_frequency_meas / number_of_holes;  // convert how many holes per second,
                                                                    // to angular fereq by scaling by the number of holes
    //angular_frequency_meas1 = raw_frequency_meas1 / number_of_holes;
    angular_frequency_meas2 = raw_frequency_meas2 / number_of_holes;
    
    // myPID.Compute();
    get_parameters();                       // Sent key parameters over Serial comms

    // if ((driver_state == ENABLE) && (pid_state == ENABLE) && (change_pull_freq == LOW)) {
    //   angular_frequency_request -= angular_frequency_pid;
    //   //set_pull_frequency("PID");
    // }
    
    // Change rotation set point, only possible when PID is disabled,
    // and only when the motor driver is enabled
    if ((change_pull_freq == HIGH) && (driver_state == ENABLE) && (pid_state == DISABLE)) {   
      
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
      }   
    }
    
    //sum = 0;
    //count = 0;
    sum1 = 0;
    count1 = 0;
    sum2 = 0;
    count2 = 0;
    
    gateCounter = 0;

    freqmeasureMillis += SAMPLE_PERIOD;
  } /* freqmeasureMillis */
    
  // Calculate 1 Hz update rate, could be done using the 16 Hz signal instead
  if (currentMillis - oneppsMillis >= PERIOD_1HZ / 2) {
    onePPS();
    oneppsMillis += PERIOD_1HZ / 2;
  } /* oneppsMillis */
    
} /* loop */

void onePPS() {
  if (semaphore_pps == LOW) {
    digitalWrite(PPSLED, HIGH);
    semaphore_pps = HIGH;
  } else if (semaphore_pps == HIGH) {
    digitalWrite(PPSLED, LOW);
    semaphore_pps = LOW;
  }
}

void gateCount() {
  int pin_state = digitalRead(GATEPIN);
  if (pin_state == HIGH && last_pin_state == LOW) {  // rising edge
    gateCounter++;
  }
  last_pin_state = pin_state;
}

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

//void setTeensyTime() {
//  
//  if (USBSERIAL.available()) {
//    // On Linux, you can use "date +T%s\n > /dev/ttyACM0" (UTC time zone!)
//    // lacal time, with TZ_adjust set to UTC offset
//    // $ TZ_adjust=10; echo T$(($(date +%s)+60*60*$TZ_adjust))> /dev/cu.usbmodem79315001
//    processSyncMessage();
//
//    if (timeStatus() != timeNotSet) {
//      // digital clock display of the time
//      USBSERIAL.print(hour());
//      printTimeDigits(minute());
//      printTimeDigits(second());
//      USBSERIAL.print(" ");
//      USBSERIAL.print(day());
//      USBSERIAL.print(" ");
//      USBSERIAL.print(month());
//      USBSERIAL.print(" ");
//      USBSERIAL.print(year()); 
//      USBSERIAL.println();
//    }
//  } 
//}

//void processSyncMessage() {
//  unsigned long pctime;
//  const unsigned long DEFAULT_TIME = 1357041600; // Jan 1 2013
//
//  if(USBSERIAL.find(TIME_HEADER)) {
//     pctime = USBSERIAL.parseInt();
//     if( pctime >= DEFAULT_TIME) { // check the integer is a valid time (greater than Jan 1 2013)
//       setTime(pctime); // Sync Arduino clock to the time received on the serial port
//       //pctime;
//     }
//  }  
//}

//void printTimeDigits(int digits){
//  // utility function for digital clock display: prints preceding colon and leading 0
//  USBSERIAL.print(":");
//  if(digits < 10)
//    USBSERIAL.print('0');
//  USBSERIAL.print(digits);
//}


//void readGateSignal() {
//  // Read Photogate signal
//  val = digitalRead(GATEPIN);
//   
//  //If photogate detects something, turn Teensy LED on
//  if ((val == HIGH) && (semaphore_gate == 0)) {
//    digitalWrite(LED, HIGH);
//    semaphore_gate = 1;
//  } else if ((val == LOW) && (semaphore_gate == 1))  {
//    //Leave LED off otherwise
//    digitalWrite(LED, LOW);
//    semaphore_gate = 0;
//  } 
//}


void recvWithStartEndMarkers() {
    // Code obtained from https://forum.arduino.cc/index.php?topic=396450
    static byte ndx = 0;
    char endMarker = END_MARKER;
    char rc;
 
    while (USBSERIAL.available() > 0 && newSerialData == false) {
        rc = USBSERIAL.read();

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
            commandProcess();
        }
     }
}

void commandProcess() {  
  char* cmd = 0;
  char temp[BUFFER_LENGTH+1];

  if (newSerialData == true) {
    strcpy(temp, receivedChars);
       
    cmd = strtok(temp, " ");
    strcpy(baseCmd, cmd);

    cmd = strtok(NULL, " ");
    if (cmd) {
      strcpy(arg1, cmd);

      cmd = strtok(NULL, " ");
      if (cmd) {
        USBSERIAL.print(F("ERROR_TOO_MANY_ARGUMENTS:"));
        USBSERIAL.println(temp);
        USBSERIAL.read();                 // empty serial input buffer
      }
    }

    if (strlen(baseCmd)) {
      if      (0 == strcmp(baseCmd, "?en"))       get_engage_driver(receivedChars);
      else if (0 == strcmp(baseCmd, "!en"))       set_engage_driver(receivedChars);   
      else if (0 == strcmp(baseCmd, "?pf"))       get_pull_frequency(receivedChars);
      else if (0 == strcmp(baseCmd, "!pf"))       set_pull_frequency(receivedChars);
      else if (0 == strcmp(baseCmd, "!sp"))       set_acc_pull_frequency(receivedChars);
      else if (0 == strcmp(baseCmd, "?sp"))       get_angular_frequency_setpoint(receivedChars);
      else if (0 == strcmp(baseCmd, "?af"))       get_angular_frequency_meas(receivedChars);
      else if (0 == strcmp(baseCmd, "?aa"))       get_angular_acceleration(receivedChars);
      else if (0 == strcmp(baseCmd, "!aa"))       set_angular_acceleration(receivedChars);
      else if (0 == strcmp(baseCmd, "?as"))       get_at_setpoint(receivedChars);
      else if (0 == strcmp(baseCmd, "?if"))       get_raw_frequency_meas(receivedChars);
//      else if (0 == strcmp(baseCmd, "?ep"))       get_engage_pid(receivedChars);
//      else if (0 == strcmp(baseCmd, "!ep"))       set_engage_pid(receivedChars);
//      else if (0 == strcmp(baseCmd, "?kp"))       get_kp(receivedChars);
//      else if (0 == strcmp(baseCmd, "!kp"))       set_kp(receivedChars);
//      else if (0 == strcmp(baseCmd, "?ki"))       get_ki(receivedChars);
//      else if (0 == strcmp(baseCmd, "!ki"))       set_ki(receivedChars);
//      else if (0 == strcmp(baseCmd, "?kd"))       get_kd(receivedChars);
//      else if (0 == strcmp(baseCmd, "!kd"))       set_kd(receivedChars);     
//      else if (0 == strcmp(baseCmd, "?pd"))       get_pid_direction(receivedChars);     
//      else if (0 == strcmp(baseCmd, "!pd"))       set_pid_direction(receivedChars);     
//      else if (0 == strcmp(baseCmd, "?pid"))      get_angular_frequency_pid(receivedChars);     
//      else if (0 == strcmp(baseCmd, "?pps"))      get_one_pps(receivedChars);     
      else if (0 == strcmp(baseCmd, "!h"))        set_number_of_holes(receivedChars);
      else if (0 == strcmp(baseCmd, "?h"))        get_number_of_holes(receivedChars);
      else if (0 == strcmp(baseCmd, "?v"))        get_software_version(receivedChars);
      else if (0 == strcmp(baseCmd, "?id"))       get_software_id(receivedChars);
      else {
        USBSERIAL.print(F("ERROR_UNKNOWN_COMMAND:"));
        finaliseError(receivedChars);
      }
    } /* if strlen(baseCmd) */
 
    newSerialData = false;
  } // if newSerialData
}

void finaliseError(char *in) {
  USBSERIAL.println(in);
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
    USBSERIAL.print(F("ERROR_GET_ENGAGE_DRIVER:"));
    finaliseError(in);  
    } else {
      USBSERIAL.println(!tmp);
    }
}

void set_engage_driver(char* in) {
  int tmp = atoi(arg1);
  
  if ( ((tmp != DISABLE) == (tmp != ENABLE))) {
    USBSERIAL.print(F("ERROR_SET_ENGAGE_DRIVER:"));
    finaliseError(in);
    
  } else if (tmp == ENABLE)  {
    digitalWrite(ENAPIN, LOW);
    driver_state = ENABLE;
    USBSERIAL.println(F("Ok"));
    
  } else if (tmp == DISABLE) {
    digitalWrite(ENAPIN, HIGH);
    driver_state = DISABLE;
    pid_state = DISABLE;
    angular_frequency_setpoint = 0;
    angular_frequency_request = 0;
    set_pull_frequency("DISABLE:");
    USBSERIAL.println(F("Ok"));
  }
}

//void get_engage_pid(char* in) {
//  boolean tmp = myPID.GetMode();                    // return: AUTOAMTIC = 1
//                                                    // return: MANUAL = 0
//  
//  if ( ((tmp != DISABLE) == (tmp != ENABLE))) {
//    USBSERIAL.print(F("ERROR_GET_ENGAGE_PID:"));
//    finaliseError(in);
//    
//    } else {
//      USBSERIAL.println(tmp);
//    }
//}

//void set_engage_pid(char* in) {
//  int tmp = atoi(arg1);
//  
//  if ( ((tmp != DISABLE) == (tmp != ENABLE)) ) {
//    USBSERIAL.print(F("ERROR_SET_ENABLE_PID:"));
//    finaliseError(in);
//    
//  } else if ((tmp == ENABLE) && (driver_state == ENABLE)) {
//    pid_state = ENABLE;
//    USBSERIAL.println(F("Ok"));
//    
//  } else if (tmp == DISABLE) {
//    pid_state = DISABLE;
//    USBSERIAL.println(F("Ok"));
//  }
//}

void get_pull_frequency(char* in) {
  USBSERIAL.println(pull_frequency);  
}

void set_pull_frequency(char* in) {
  /*
   * Here is were we set the actual motor pull frequency
   */
  float tmp = angular_frequency_request * GEAR_RATIO * PULL_RATIO;
  
  if (tmp < PULL_FREQUENCY_MIN || tmp > PULL_FREQUENCY_MAX) {
    USBSERIAL.print(F("ERROR_PULL_FREQUENCY_RANGE:"));
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
    USBSERIAL.print(F("ERROR_ACC_PULL_FREQUENCY_RANGE:"));
    finaliseError(in);
    
  } else if (angular_frequency_setpoint != tmp) {
    delta = angular_acceleration * SAMPLE_PERIOD / 1000;

    if (tmp < angular_frequency_setpoint) {
      delta = -1 * delta; 
    }

    angular_frequency_setpoint = tmp;

    pid_state = DISABLE;
    change_pull_freq = HIGH;   
    
    //setpointMillis = millis();   
  }  
  USBSERIAL.println(F("Ok"));
}

void get_angular_frequency_setpoint(char* in) {
  USBSERIAL.println(angular_frequency_setpoint);
}

void get_at_setpoint(char* in) {
  if (change_pull_freq == LOW) {
    USBSERIAL.println(ENABLE);
  }
  if (change_pull_freq == HIGH) {
    USBSERIAL.println(DISABLE);
  }
}

//void get_one_pps(char* in) {
//  USBSERIAL.println(semaphore_pps);
//}

void get_raw_frequency_meas(char* in) {
  USBSERIAL.println(raw_frequency_meas);
}

void get_angular_frequency_meas(char* in) {
  USBSERIAL.println(angular_frequency_meas);
}

void get_angular_acceleration(char* in) {
  USBSERIAL.println(angular_acceleration);
}

void set_angular_acceleration(char* in) {
  float tmp = atof(arg1);
  
  if (tmp < ANGULAR_ACCELERATION_MIN || tmp > ANGULAR_ACCELERATION_MAX) {
    USBSERIAL.print(F("ERROR_ANGULAR_ACCELERATION_RANGE:"));
    finaliseError(in);
  } else {
    angular_acceleration = tmp;
    USBSERIAL.println(F("Ok"));
  }
}

//void get_kp(char* in) {
//  USBSERIAL.println(myPID.GetKp());
//}

//void set_kp(char* in) {
//  int tmp = atof(arg1);
//  
//  if (tmp < KP_MIN || tmp > KP_MAX) {
//    USBSERIAL.print(F("ERROR_KP:"));
//    finaliseError(in);
//  } else {
//    Kp = tmp;
//    myPID.SetTunings(Kp, Ki, Kd);
//    USBSERIAL.println(F("Ok"));
//  }  
//}

//void get_ki(char* in) {
//  USBSERIAL.println(myPID.GetKi());
//}

//void set_ki(char* in) {
//  int tmp = atof(arg1);
//  
//  if (tmp < KI_MIN || tmp > KI_MAX) {
//    USBSERIAL.print(F("ERROR_KI:"));
//    finaliseError(in);
//  } else {
//    Ki = tmp;
//    myPID.SetTunings(Kp, Ki, Kd);
//    USBSERIAL.println(F("Ok"));
//  }  
//}

//void get_kd(char* in) {
//  USBSERIAL.println(myPID.GetKd());
//}

//void set_kd(char* in) {
//  int tmp = atof(arg1);
//  
//  if (tmp < KD_MIN || tmp > KD_MAX) {
//    USBSERIAL.print(F("ERROR_KD:"));
//    finaliseError(in);
//  } else {
//    Kd = tmp;
//    myPID.SetTunings(Kp, Ki, Kd);
//    USBSERIAL.println(F("Ok"));
//  }  
//}

//void get_pid_direction(char* in) {
//  int tmp = myPID.GetDirection();
//  USBSERIAL.println(tmp);
//}

//void set_pid_direction(char* in) {
//  int tmp = atoi(arg1);
//
//  if ( ((tmp != 1) == (tmp != 0))) {
//    USBSERIAL.print(F("ERROR_PID_DIRECTION:"));
//    finaliseError(in);
//    
//  } else if (tmp == 0) {
//    myPID.SetControllerDirection(DIRECT);
//    USBSERIAL.println(F("Ok"));
//    
//  } else if (tmp == 1) {
//    myPID.SetControllerDirection(REVERSE);
//    USBSERIAL.println(F("Ok"));
//  }
//}

//void get_angular_frequency_pid(char* in) {
//  USBSERIAL.println(angular_frequency_pid);
//}

void get_number_of_holes(char* in) {
  USBSERIAL.println(number_of_holes);
}

void set_number_of_holes(char* in) {
  int tmp = atoi(arg1);
  
  if (tmp < NUM_OF_HOLES_MIN || tmp > NUM_OF_HOLES_MAX) {
    USBSERIAL.print(F("ERROR_NUMBER_OF_HOLES_RANGE:"));
    finaliseError(in);
  } else {
    number_of_holes = tmp;
    USBSERIAL.println(F("Ok"));
  }  
}

void get_software_version(char* in) {
  USBSERIAL.println(SOFTWARE_VERSION);
}

void get_software_id(char* in) {
  USBSERIAL.println(SOFTWARE_ID);
}

void get_parameters() {
  char buffer [50];
  
  // Slow Controls
  /*
  boolean engage_driver = digitalRead(ENAPIN);
  boolean engage_pid = myPID.GetMode();
  number_of_holes;
  !change_pull_freq;
  angular_frequency_setpoint;
  myPID.GetKp();
  myPID.GetKi();
  myPID.GetKd()
  myPID.GetDirection();
  angular_acceleration;
  */
  
  // Real-Time controls
  sprintf(buffer, "%.3f,%.3f,%.3f,%.3f,%.3f,%d,%.3f", 
    raw_frequency_meas,
    angular_frequency_meas, 
    raw_frequency_meas2,
    angular_frequency_meas2, 
    pull_frequency, 
    semaphore_pps, 
    angular_frequency_pid);
  HWSERIAL.println(buffer);
  
  }
