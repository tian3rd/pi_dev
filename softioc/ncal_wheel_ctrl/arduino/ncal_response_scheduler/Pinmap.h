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

const int FREQ1PIN = 9;                   // FreqMeasureMulti first sensor pin 9
const int FREQ2PIN = 10;                  // FreqMeasureMulti first sensor pin 10
