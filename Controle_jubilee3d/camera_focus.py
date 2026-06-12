import cv2
import numpy as np
import time


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

focus_value = 0



def on_focus_change(value):
    global focus_value

    focus_value = value

    cap.set(cv2.CAP_PROP_FOCUS, focus_value)

    print(f"Foco: {focus_value}")



cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)

cv2.createTrackbar(
    'Focus',
    'Camera',
    0,      
    255,   
    on_focus_change
)

print("Pressione 'q' para sair.")



while True:

    ret, frame = cap.read()

    if not ret:
        print("Erro ao capturar frame.")
        break

    cv2.imshow('Camera', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()