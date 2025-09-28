M290 R0 S0                 ; Reset baby stepping
M561                       ; Disable any Mesh Bed Compensation
G30 P0 X160 Y360 Z-99999   ; probe near back leadscrew
G30 P1 X20 Y70 Z-99999   ; probe near front left leadscrew
G30 P2 X295 Y70 Z-99999 S3  ; probe near front right leadscrew and calibrate 3 motors
G29 S1                     ; Enable Mesh Bed Compensation
