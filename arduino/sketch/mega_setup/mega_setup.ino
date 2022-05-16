#include <Arduino.h>

const int NUM_PORTS = 32;        // for mega, use 32+32 pins; (for uno, set this to 8)
const int START_OUTPUT_PIN = 2;  // output pins range from D2 to D9
const int END_OUTPUT_PIN = START_OUTPUT_PIN + NUM_PORTS - 1;
const int START_INPUT_PIN = END_OUTPUT_PIN + 1;  // input pins range from D10 to D13 plus A0 to A3
const int END_INPUT_PIN = START_INPUT_PIN + NUM_PORTS - 1;
const int BAUD_RATE = 9600;
const int NUM_GAIN_PORTS = 4;
const int NUM_FILTER_PORTS = 4;
const int NUM_CHS = NUM_PORTS / (NUM_GAIN_PORTS + NUM_FILTER_PORTS);
const int DELAY_TIME = 20; // delay for 20ms for set operations

/*
 * Initialize pins as OUTPUTs and INPUTs
 */
void init_pins() {
  // inversed logic for output pins
  for (int pin = START_OUTPUT_PIN; pin <= END_OUTPUT_PIN; pin++) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
  }
  // by default, the pinmode is INPUT
  for (int pin = START_INPUT_PIN; pin <= END_INPUT_PIN; pin++) {
    pinMode(pin, INPUT);
    digitalWrite(pin, LOW);
  }
}

// initial setup for arduino
void setup() {
  Serial.begin(BAUD_RATE);
  init_pins();
  // set timeout for Serial response as 1000ms
  Serial.setTimeout(1000);
  // wait for the settings to be applied in 1000ms
  delay(1000);
}

/*
 * @brief Read the values of the input pins
 * @param start Start pin number (pin ranges from START_OUTPUT_PIN to END_INPUT_PIN)
 * @param end End pin number, end >= start
 * @returns a string of pin values
 */
String read_pins(int start, int end) {
  String result = "";
  for (int pin = start; pin <= end; pin++) {
    int status = digitalRead(pin);
    result += status;
  }
  // Serial.println(result);
  return result;
}

/*
 * @brief Read the values of a certain port ()  * @brief Write the values of the output pins
 * @param start Start port number (port ranges from 0 to NUM_PORTS * 2 - 1)
 * @returns an integer (1: HIGH, 0: LOW) to represent the port status
 */
int read_port(int port) {
  int pin = START_OUTPUT_PIN + port;
  int result = digitalRead(pin);
  // Serial.println(result);
  return result;
}

/*
 * @breif Set the port and corresponding pin value
 * @param port Port number of the VGA board
 * @param value HIGH or LOW voltage to set the port to
 * @returns True if set successfully, False otherwise
 */
bool set_port(int port, int value) {
  int pin = START_OUTPUT_PIN + port;
  digitalWrite(pin, value);
  delay(DELAY_TIME);
  if (read_port(port) == value) {
    // Serial.println("OK");
    return true;
  } else {
    // Serial.println("ERROR");
    return false;
  }
}

/*
 * @breif Read all pin status
 * @returns a string of pin values
 */
String read_all() {
  String result = read_pins(START_OUTPUT_PIN, END_INPUT_PIN);
  // Serial.println(result);
  return result;
}

/*
 * @breif Read all output pins (0-31 ports on the VGA board)
 * @returns a string of pin values for output pins
 */
String read_outputs() {
  String result = read_pins(START_OUTPUT_PIN, END_OUTPUT_PIN);
  // Serial.println(result);
  return result;
}

/*
 * @brief Set the pin status based on the command string
 * @param cmd Command with NUM_PORTS characters to set for the output pins
 * @returns True if set successfully, False otherwise
 */
bool set_outputs(String cmd) {
  if (cmd.length() != NUM_PORTS) {
    // Serial.println("Invalid command");
    return false;
  }
  for (int pin = START_OUTPUT_PIN; pin <= END_OUTPUT_PIN; pin++) {
    int status = cmd.charAt(pin - START_OUTPUT_PIN) - '0';
    digitalWrite(pin, status);
    delay(DELAY_TIME);
    if (status != digitalRead(pin)) {
      // Serial.println("Failed to set pin");
      return false;
    }
  }
  return true;
}

/*
 * @breif Read all inputs pins (32-63 ports on the VGA board)
 * @returns a string of pin values for input pins
 */
String read_inputs() {
  String result = read_pins(START_INPUT_PIN, END_INPUT_PIN);
  // Serial.println(result);
  return result;
}

// the loop function runs over and over again forever
void loop() {
  String cmd;
  if (Serial.available()) {
    // read the command from Serial:
    cmd = Serial.readStringUntil('\n');
    if (cmd.startsWith("RA")) {  // 'RA' to read all pins
      Serial.println(read_all());
    } else if (cmd.startsWith("ROUTS")) {  // 'ROUTS' to read all output pins
      Serial.println(read_outputs());
    } else if (cmd.startsWith("RINTS")) {  // 'RINTS' to read all input pins
      Serial.println(read_inputs());
    } else if (cmd.startsWith("R")) {  // 'R' to read an indivisual pin
      int port = cmd.substring(1, 3).toInt();
      Serial.println(read_port(port));
    } else if (cmd.startsWith("WOUTS")) {  // 'WOUTS' to write all output pins
      String outputs_cmd = cmd.substring(5);
      if (set_outputs(outputs_cmd)) {
        Serial.println("OK");
      } else {
        Serial.println("ERROR");
      }
    } else if (cmd.startsWith("W")) {  // 'W' to write a value to a certain pin/port
      int port = cmd.substring(1, 3).toInt();
      int value = cmd.substring(3).toInt();
      if (set_port(port, value)) {
        Serial.println("OK");
      } else {
        Serial.println("ERROR");
      }
    }
  }
}
