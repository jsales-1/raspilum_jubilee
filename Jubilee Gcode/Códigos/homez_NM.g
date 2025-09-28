; Home Z Axis

;if !move.axes[3].homed
;  M291 R"Cannot Home Z" P"U axis must be homed before Z to prevent damage to tool. Press OK to home U or Cancel to abort" S3
;  M98 P"homeu.g"

; RRF3 does not permit Z homing without x&y being homed first. Popup window for convenience.
;if !move.axes[0].homed || !move.axes[1].homed
;  M291 R"Cannot Home Z" P"X&Y Axes must be homed before Z for probing. Press OK to home X&Y or Cancel to abort" S3
;  M98 P"homey.g"
;  M98 P"homex.g"

;if state.currentTool != -1
;  M84 U
;  M291 R"Cannot Home Z" P"Tool must be deselected before homing. U has been unlocked, please manually dock tool and press OK to continue or Cancel to abort" S3
;  M98 P"homeu.g"

M290 R0 S0              ; Reset baby stepping

G91                     ; Relative positioning mode
G1 H2 Z5 F5000          ; Move bed down (raise nozzle) by 5mm
G90                     ; Back to absolute positioning

G90 G1 X160 Y200 F10000     ; Move to probe position (adjusted to avoid magnet screw)

M558 F500               ; Set fast probing speed
G30                     ; Probe Z (single touch)

G91                     ; Switch to relative mode
G1 Z2 F200              ; Move bed down 2mm (back off slightly)
G90                     ; Back to absolute mode
