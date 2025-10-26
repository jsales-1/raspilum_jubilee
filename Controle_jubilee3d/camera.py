import cv2
import numpy as np
import time



cap = cv2.VideoCapture(3)
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

    cv2.imshow('Camera', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()