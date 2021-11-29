/* ncal_source
 * 
 * Using an Arduino MEGA 2560
 * 
 * FreqMeasure is done on pin 49 (fixed), comes from
 * pin 29 (PULL)
 * 
 * Output is put on pin 6, connected to pin D05 on T3.5
 * 
 */

#include <FreqMeasure.h>
#include <Tone.h>

const float SAMPLE_PERIOD = 31UL;

//Initializing LED Pin
int sig1_pin = 6;
int sig2_pin = 7;

//int pull_pin = 3; // PWM pin

double pullFreq = 0;
double freqRead = 0;
double sum = 0;
int count = 0;

double raw_frequency_meas;

unsigned long currentMillis;
unsigned long freqmeasureMillis;

Tone sigout1;
Tone sigout2;

void setup() {
  //Declaring LED pin as output
  //pinMode(sig_pin, OUTPUT);
  //pinMode(pull_pin, INPUT);
  //analogWrite(sig_pin, 20);

  sigout1.begin(sig1_pin);
  sigout2.begin(sig2_pin);

  FreqMeasure.begin();
}



void loop() {
  //pullFreq = digitalRead(pull_pin);

  currentMillis = millis();

  // Check if there is a signal on pin 3, 
  // to make the freq measurement available 
  if (FreqMeasure.available()) {
    
    // average several reading, on
    // pin 49 on the MEGA 2560
    freqRead = FreqMeasure.read();
    sum = sum + freqRead;

    count++;

    // Calculate the raw and angular frequency signals, and
    // Run the PID if enabled and not changing setpoint (=change_pull_freq)
    if (currentMillis - freqmeasureMillis >= SAMPLE_PERIOD) {
      raw_frequency_meas = FreqMeasure.countToFrequency(sum / count);  
      sigout1.play(raw_frequency_meas);
      sigout2.play(raw_frequency_meas);
           
      sum = 0;
      count = 0;
      freqmeasureMillis += SAMPLE_PERIOD;
    }
  } 
  
}
