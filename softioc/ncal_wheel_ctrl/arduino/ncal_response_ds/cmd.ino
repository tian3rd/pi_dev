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
 * ?as        int     returns at setpoint, 1 = yes, or 0 = no  - EPICS
 * ?if        float   returns frequency measurement at interval period (16Hz or 32 Hz)  - EPICS
 * ?af        float   returns the latest averaged angular frequency (16Hz or 32 Hz)  - EPICS
 * ?aa        float   returns the acceleration gain, rev/s^2 (or Hz /s]  - EPICS
 * !aa        float   set the acceleration gain [default 0.08 per 31.25 ms]  - EPICS
 * ?ep        int     returns if the PID is enabled (1) or disabled (0)  - EPICS
 * !ep        int     set the PID to enable (1) or disable (0)  - EPICS
 * ?kp        float   returns the PID proportional gain  - EPICS
 * !kp        float   set the PID proportional gain  - EPICS
 * ?ki        float   returns the PID integral gain  - EPICS
 * !ki        float   set the PID integral gain  - EPICS
 * ?kd        float   returns the PID diffirential gain  - EPICS
 * !kd        float   set the PID diffirential gain  - EPICS
 * ?pd        int     return PID direction (1) reverse, (0) direct  - EPICS
 * !pd        int     set the PID direction (0) direct or (1) reverse  - EPICS
 * ?pid       int     get PID calculated angular frequency correction signal  - EPICS 
 * ?pps       int     get 1 PPS, rising edge is 1 sec apart (so 2 Hz pulse)  - EPICS
 * ?h         int     returns the current number of holes for the photgate  - EPICS
 * !h         int     set the number of holes for the photogate
 * ?v         string  returns version string
 * ?id        0       returns identification string
 * other              returns "ERROR_UNKNOWN_COMMANT:text"
 * 
 * Communications Parameters
 * term                     value
 * communications rate      250000
 * line terminator          \n
 * buffer length (chars)    32
 * command length (chars)   16
 * 
 */
