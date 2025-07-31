import cv2
import numpy as np


class camera_tool:
    def __init__(self, machine=None):
        self.installed = False
        self.machine = machine
        self.move_velocity = 10000

    def install(self):
        self.machine.move_xyz_absolute(y=220, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=302, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=7, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=50, y=120, velocity=self.move_velocity)

    def uninstall(self):
        self.machine.move_xyz_absolute(y=90, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=302, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(y=7, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=50, y=120, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")

    def photo(self, filename='captura.jpg',video_index=0):
        cap = cv2.VideoCapture(video_index)
        if not cap.isOpened():
            return

        ret, frame = cap.read()
        if not ret:
            cap.release()
            return

        cv2.imwrite(filename, frame)

        cap.release()

