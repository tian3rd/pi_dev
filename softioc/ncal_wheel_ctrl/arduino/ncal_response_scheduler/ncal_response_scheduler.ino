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
#include <FreqMeasureMulti.h>                   // see https://github.com/PaulStoffregen/FreqMeasureMulti, using pin 9 and 10

// set this to the hardware serial port you wish to use
#define USBSERIAL Serial                        // Used for general control and interface
#define HWSERIAL Serial1                        // Used for Real-Time data comms,
                                                // Rx pin 0 (T3.5) -> Tx pin 8 (RPI),
                                                // Tx pin 1 (T3.5) -> Rx pin 10 (RPI)

const String SOFTWARE_VERSION = "2020-10-28";
const String SOFTWARE_ID = "ncal_response_scheduler";

FreqMeasureMulti freq1;
FreqMeasureMulti freq2;

#include "Constants.h"
#include "Pinmap.h"


/* 
 * Set variables
 *
 */
bool newSerialData = false;               // Serial data semaphore
char receivedChars[BUFFER_LENGTH+1];      // received character string
char baseCmd[COMMAND_LENGTH+1];           // array for holding the command instruction
char arg1[COMMAND_LENGTH+1];              // array for holding the command argument

bool semaphore_pid = LOW;
bool semaphore_pps = LOW;
static int last_pin_state = LOW;

double sum1 = 0;
double sum2 = 0;
int count1 = 0;
int count2 = 0;

int gateCounter = 0;
float delta = 0;                          // difference in PULL frequency

bool driver_state = DISABLE;              // State of Motor Dirver
bool change_pull_freq = false;
bool at_setpoint = false;

float angular_acceleration = ANGULAR_ACCELERATION_DEFAULT;

double angular_frequency_setpoint = ANGULAR_FREQUENCY_DEFAULT;         // Set point of the angular frequency
double angular_frequency_request = ANGULAR_FREQUENCY_DEFAULT;
double angular_frequency_pid = ANGULAR_FREQUENCY_DEFAULT;

double angular_frequency_meas1 = 0;              // the period of rotation of the wheel, Hz
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

typedef struct {
    uint32_t tStart;
    uint32_t tTimeout;
} t;

//Tasks and their Schedules.
t t_func1hz = {0, PERIOD_1HZ};  //Run every 1 second
t t_func16hz = {0, PERIOD_16HZ}; //Run every 62 ms
t t_func32hz = {0, PERIOD_32HZ}; //Run every 31 ms
//t t_func16khz = {0, PERIOD_16KHZ}; //Run every 61 us

bool tCheck (t *t ) {
  if (millis() > t->tStart + t->tTimeout) {
    return true;  
  }
  return false;
}

void tRun (t *t) {
    t->tStart = millis();
}

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
  
  USBSERIAL.begin(USB_BAUD);              // establish USB command communication
  HWSERIAL.begin(DATA_BAUD);              // establish Serial parameter communication

  resetBuffer();                          // reset all communication buffers

  USBSERIAL.print(F("cmd_response started: "));
  USBSERIAL.println(FreeMem());              // prints free memory, as a signature.

  freq1.begin(FREQ1PIN);
  freq2.begin(FREQ2PIN);

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

  if (tCheck(&t_func1hz)) {
    func1hz();
    tRun(&t_func1hz);
  }
  
  if (tCheck(&t_func16hz)) {
    func16hz();
    tRun(&t_func16hz);
  }

  if (tCheck(&t_func32hz)) {
    func32hz();
    tRun(&t_func32hz);
  }

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
  
  gateCounter++;

} /* loop */


void func1hz (void) {
  //This executes every 1 second.

  onePPS();
}

void func16hz (void) {
  //This executes every 62 ms.

  recvWithStartEndMarkers();              // read command 
  commandProcess();                       // extract instruction and argument
}

void func32hz (void) {
  //This executes every 31 ms.

  if (sum1 != 0) {
    raw_frequency_meas1 = freq1.countToFrequency(sum1 / count1);
  }
  if (sum2 != 0) {
    raw_frequency_meas2 = freq2.countToFrequency(sum2 / count2);
  }
  
  angular_frequency_pid = gateCounter;
                                                                  
  angular_frequency_meas1 = raw_frequency_meas1 / number_of_holes;  // convert how many holes per second,
                                                                    // to angular fereq by scaling by the number of holes
  angular_frequency_meas2 = raw_frequency_meas2 / number_of_holes;
  
  get_parameters();                       // Sent key parameters over Serial comms
 
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
  
  sum1 = 0;
  count1 = 0;
  sum2 = 0;
  count2 = 0;
  
  gateCounter = 0;
}

void onePPS() {
  if (semaphore_pps == LOW) {
    digitalWrite(PPSLED, HIGH);
    semaphore_pps = HIGH;
  } else if (semaphore_pps == HIGH) {
    digitalWrite(PPSLED, LOW);
    semaphore_pps = LOW;
  }
}

void get_parameters() {
  char buffer [50];
  
  // Real-Time controls
  sprintf(buffer, "%.3f,%.3f,%.3f,%.3f,%.3f,%d,%.3f", 
    raw_frequency_meas1,
    angular_frequency_meas1, 
    raw_frequency_meas2,
    angular_frequency_meas2, 
    pull_frequency, 
    semaphore_pps, 
    angular_frequency_pid);
  HWSERIAL.println(buffer);
  
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
