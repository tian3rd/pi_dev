/*
 * all command lowercase
 * integers must be in decimal
 * ? commands return an integer, this is the get command
 * ! command return an Ok
 * Errors starting with ERROR_ will substitute for expedected output
 * 
 * USB Command interface
 * 
 * Commands with - EPICS at the end are integrated in to EPICS IOC and MEDM screen
 * 
 * ---
 * command    value   action
 * ?en        int     returns if the driver is enabled (1) or disabled (0)  - EPICS
 * !en        int     set the driver to enable (1) or disable (0)  - EPICS
 * ?pf        float   returns the current motor PULL frequency  - EPICS
 * !pf        float   set new motor PULL frequency
 * ?sp        float   returns the angular frequency setpoint  - EPICS
 * !sp        float   set new PULL frequency, linear interpolate from current to new  - EPICS
 * ?af        float   returns the latest averaged angular frequency of sensor 1 (16Hz or 32 Hz)  - EPICS
 * ?aa        float   returns the acceleration gain, rev/s^2 (or Hz /s]  - EPICS
 * !aa        float   set the acceleration gain [default 0.08 per 31.25 ms]  - EPICS
 * ?as        int     returns at setpoint, 1 = yes, or 0 = no  - EPICS
 * ?if        float   returns frequency measurement at interval period (16Hz or 32 Hz)  - EPICS
 * ?h         int     returns the current number of holes for the photgate  - EPICS
 * !h         int     set the number of holes for the photogate
 * ?v         string  returns version string
 * ?id        strin   returns identification string
 * other              returns "ERROR_UNKNOWN_COMMANT:text"
 * 
 * Communications Parameters
 * term                     value
 * communications rate      115200
 * line terminator          \n
 * buffer length (chars)    32
 * command length (chars)   16
 * 
 */
