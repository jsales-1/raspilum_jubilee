"""
Captura de vídeo da câmera, detecção de círculos e salvamento de frames.

- Converte cada frame para escala de cinza e aplica desfoque Gaussiano.
- Detecta círculos usando a Transformada de Hough.
- Desenha o maior círculo detectado e seu centro.
- Permite salvar frames pressionando 's'.
- Pressione 'q' para sair.
"""

import cv2
import numpy as np
from datetime import datetime

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

print("Pressione 'q' para sair.")
cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame.")
        break

    # Converte para escala de cinza e aplica desfoque
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detecta círculos no frame
    circles = cv2.HoughCircles(
        gray_blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=10,
        maxRadius=210
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles = sorted(circles, key=lambda x: x[2], reverse=True)
        
        for circle in circles:
            x, y, r = circle

            # Desenha o círculo e seu centro
            cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
            cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
            cv2.putText(frame, f"{r}", (x - 40, y - r - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Mostra o frame processado
    cv2.imshow('Camera', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    if key == ord('s'):
        # Salva o frame atual com timestamp
        now = datetime.now()
        current_time_hms = now.strftime("%H:%M:%S")
        filename = f'{current_time_hms}.png'
        cv2.imwrite(filename, frame)

cap.release()
cv2.destroyAllWindows()
