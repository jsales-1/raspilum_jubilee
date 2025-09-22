import lgpio
import time

class Gripper:
    """
    Classe para controle de um gripper servo-controlado integrado
    na Jubilee.

    Esta classe permite instalar e desinstalar o gripper, além de 
    controlar a abertura e fechamento do mesmo através de um servo motor.

    Attributes:
        machine: Objeto que representa a máquina Jubilee, permitindo
            enviar comandos G-Code e realizar movimentações.
        servo_pin (int): Pino GPIO utilizado para o controle do servo.
        parking_position_x (float): Posição X de estacionamento/acoplamento.
        parking_position_y (float): Posição Y de estacionamento/acoplamento.
        handle (int): Manipulador do chip GPIO utilizado pelo `lgpio`.
        move_velocity (int): Velocidade dos movimentos em mm/min.
    """

    def __init__(self, machine, servo_pin=13, parking_position_xy=(40, 7)):
        """
        Inicializa o gripper e posiciona o eixo Z em uma altura segura.

        Args:
            machine: Instância de controle da máquina Jubilee.
            servo_pin (int, optional): Pino GPIO do servo motor. Default é 13.
            parking_position_xy (tuple, optional): Coordenadas (X, Y) para 
                estacionamento do gripper. Default é (40, 7).
        """
        self.parking_position_x, self.parking_position_y = parking_position_xy
        self.handle = lgpio.gpiochip_open(0)
        self.servo_pin = servo_pin
        self.machine = machine
        self.move_velocity = 10000

        self.machine.gcode("M208 Z100:300")
        if self.machine.position[2] < 100:
            self.machine.move_xyz_absolute(z=100)

    def install(self):
        """
        Instala o gripper na máquina Jubilee.

        Este método move o cabeçote para as coordenadas específicas
        necessárias para acoplar o gripper ao sistema. As coordenadas
        foram determinadas empiricamente e podem ser ajustadas conforme
        necessário.
        """
        self.machine.protect_tools(on=False)
        self.machine.move_xyz_absolute(y=220, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)

        if self.machine.mode_protect_tools:
            self.machine.protect_tools(on=False)

    def uninstall(self):
        """
        Desinstala o gripper da máquina Jubilee.

        Este método move o cabeçote para as coordenadas necessárias
        para desacoplar o gripper do sistema.
        """
        self.machine.protect_tools(on=False)
        self.machine.move_xyz_absolute(y=90, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")

        if self.machine.mode_protect_tools:
            self.machine.protect_tools(on=False)

    def set_angle(self, angle):
        """
        Define o ângulo do servo motor que controla o gripper.

        Args:
            angle (float): Ângulo desejado em graus (0 a 180).
        """
        duty = 2.5 + (angle / 180.0) * 10.0
        lgpio.tx_pwm(self.handle, self.servo_pin, 50, duty)

    def begin(self):
        """
        Abre o manipulador GPIO para permitir controle do servo.
        """
        self.handle = lgpio.gpiochip_open(0)

    def end(self):
        """
        Fecha o manipulador GPIO, liberando o recurso.
        """
        lgpio.gpiochip_close(self.handle)

    def open(self):
        """
        Abre o gripper para um ângulo padrão (30°).
        """
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(30)
        time.sleep(0.5)
        self.end()

    def open_angles(self, angle):
        """
        Abre o gripper em um ângulo específico.

        Args:
            angle (float): Ângulo desejado em graus (0 a 180).
        """
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(angle)
        time.sleep(0.5)
        self.end()

    def close(self):
        """
        Fecha completamente o gripper (0°).
        """
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(0)
        time.sleep(0.5)
        self.end()
