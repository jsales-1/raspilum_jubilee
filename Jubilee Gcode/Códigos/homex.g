; Home X Axis

; In case homex.g is called in isolation, ensure 
; (1) U axis is homed (which performs tool detection and sets machine tool state to a known state) and 
; (2) Y axis is homed (to prevent collisions with the tool posts)
; (3) Y axis is in a safe position (see 2)
; (4) No tools are loaded.
; Ask for user-intervention if either case fails.

G90                     ; Set absolute mode

;if !move.axes[3].homed
;  M291 R"Cannot Home X" P"U axis must be homed before X to prevent damage to tool. Press OK to home U or Cancel to abort" S3
;  M98 P"homeu.g"

;if !move.axes[1].homed
;  M291 R"Cannot Home X" P"Y axis must be homed before x to prevent damage to tool. Press OK to home Y or Cancel to abort" S3
;  M98 P"homey.g"
  
;if move.axes[1].userPosition >= 305
;  G0 Y305 F20000       ; Rapid to safe y position

;if state.currentTool != -1
;  M84 U
;  M291 R"Cannot Home X" P"Tool must be deselected before homing. U has been unlocked, please manually dock tool and press OK to continue or Cancel to abort" S3
;  M98 P"homeu.g"
  
G91                     ; Modo relativo
G1 H2 Z10 F5000         ; Sobe a mesa (ajuste opcional)

G1 H1 X-400 F3000       ; Busca fim de curso no lado negativo (esquerda)
G1 X-4 F600              ; Afastamento do fim de curso
G1 H1 X10 F600         ; Segunda busca lenta do fim de curso
G1 H2 Z10 F5000         ; Sobe a mesa (ajuste opcional)
G90                     ; Modo absoluto
