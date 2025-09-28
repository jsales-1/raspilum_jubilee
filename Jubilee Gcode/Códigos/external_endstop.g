; Verifica se o endstop de Z está acionado
if sensors.endstops[2].triggered   ; 0=X, 1=Y, 2=Z
  G91                            ; Modo relativo
  G1 Z5 F600                     ; Sobe 5mm
  G90                            ; Volta ao modo absoluto
