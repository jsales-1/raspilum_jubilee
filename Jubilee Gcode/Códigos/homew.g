G91              ; relative moves
G1 W-200 F800 H1 ; big, slow negative move to look for endstop
G1 W200 F600     ; back off endstop
G1 W-10 F600 H1  ; find endstop again, slower
G90              ; absolute moves
G1 W0.5 F600     ; move to a position of 0.5 to start