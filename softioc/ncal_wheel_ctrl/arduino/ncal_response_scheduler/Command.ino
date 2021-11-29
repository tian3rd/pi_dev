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
  USBSERIAL.println(angular_frequency_meas1);
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
