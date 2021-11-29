/*
 * Constants
 */
 
const byte BUFFER_LENGTH = 32;
const int COMMAND_LENGTH = 16;

const char END_MARKER = '\n';

const long USB_BAUD = 115200;
const long DATA_BAUD = 115200;

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

const int NUMBER_OF_HOLES_DEFAULT = 650;          // number of holes for the photo sensos
const int NUM_OF_HOLES_MIN = 1;
const int NUM_OF_HOLES_MAX = 1000;

const uint32_t PERIOD_1HZ = 1000UL;                  // 1 Hz update period, in milliseconds
const uint32_t PERIOD_16HZ = 62UL;                   // 16 Hz update period, in milliseconds
const uint32_t PERIOD_32HZ = 31UL;                   // 32 Hz update period, in milliseconds
const uint32_t PERIOD_16KHZ = 61UL;                   // 16 kHz update period, in useconds
const uint32_t SAMPLE_PERIOD = PERIOD_32HZ;
