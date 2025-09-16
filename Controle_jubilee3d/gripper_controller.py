import lgpio
import time

class Gripper:
    def __init__(self,machine,servo_pin=13):

        self.handle = lgpio.gpiochip_open(0)
        self.servo_pin = servo_pin
        self.machine = machine
        self.move_velocity = 10000

        self.machine.gcode("M208 Z100:300")
        if self.machine.position2[2]<100:
            self.machine.move_xyz_absolute(z=100)
        

    def install(self):
        """
        Instala a ferramenta da câmera na máquina.

        Este método move o cabeçote para as coordenadas específicas
        necessárias para acoplar a câmera ao sistema Jubilee. As
        Coodernadas foram descobertas empíricamente e podem ser 
        alteradas se necessário.
        """
        self.machine.protect_tools(on=False)
        
        self.machine.move_xyz_absolute(y=220, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=40, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=7, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=70, y=120, velocity=self.move_velocity)

        if self.machine.mode_protect_tools:
            self.machine.protect_tools(on=False)

    def uninstall(self):
        """
        Remove a ferramenta da câmera da máquina.

        Este método move o cabeçote para as coordenadas específicas
        necessárias para desacoplar a câmera do sistema Jubilee.
        """
        self.machine.protect_tools(on=False)

        self.machine.move_xyz_absolute(y=90, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=40, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(y=7, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=70, y=120, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")

        if self.machine.mode_protect_tools:
            self.machine.protect_tools(on=False)



    def set_angle(self,angle):
        # Converte ângulo para duty cycle (0°=2.5%, 180°=12.5%)
        duty = 2.5 + (angle / 180.0) * 10.0
        lgpio.tx_pwm(self.handle, self.servo_pin, 50, duty)

    def end(self):
        lgpio.gpiochip_close(self.handle)
    
    def begin(self):
        self.handle = lgpio.gpiochip_open(0)

    
    def open(self):
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(30)
        time.sleep(0.5)
        self.end()
    
    def open_angles(self,angle):
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(angle)
        time.sleep(0.5)
        self.end()

    def close(self):
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(0)
        time.sleep(0.5)
        self.end()