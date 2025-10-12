import lgpio
import time


class Gripper:
    """
    Classe para controle de um gripper servo-controlado integrado
    na Jubilee.

    Esta classe segue a mesma lógica de funcionamento da `camera_tool`,
    incluindo controle de instalação, desinstalação e verificação do
    estado atual da ferramenta.
    """

    def __init__(self, machine, servo_pin=13, parking_position_xy=(40, 7), move_velocity=10000):
        """
        Inicializa o gripper e define parâmetros de operação.

        Args:
            machine: Instância de controle da máquina Jubilee.
            servo_pin (int, optional): Pino GPIO do servo motor. Default é 13.
            parking_position_xy (tuple, optional): Coordenadas (X, Y) para 
                estacionamento do gripper. Default é (40, 7).
            move_velocity (int, optional): Velocidade padrão de movimentação (mm/min).
        """
        self.name = "Gripper"
        self.parking_position_x, self.parking_position_y = parking_position_xy
        self.servo_pin = servo_pin
        self.machine = machine
        self.move_velocity = move_velocity
        self.installed = False
        self.handle = None

        # Garante que o eixo Z esteja em altura segura antes de qualquer acoplamento
        self.machine.gcode("M208 Z100:300")
        if self.machine.position[2] < 100:
            self.machine.move_xyz_absolute(z=100)

    def install(self):
        """
        Instala o gripper na máquina Jubilee.

        Move o cabeçote até as coordenadas específicas para acoplar o gripper.
        Só executa se nenhuma outra ferramenta estiver instalada.
        """
        if self.machine.tool is None:
            self.machine.protect_tools(on=False)

            # Sequência de acoplamento (coordenadas empíricas)
            self.machine.move_xyz_absolute(y=220, velocity=self.move_velocity)
            self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=self.move_velocity)
            self.machine.gcode("G0 U70")
            self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=self.move_velocity)
            self.machine.gcode("G0 U0")
            self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)

            # Reativa proteção de ferramentas, se necessário
            if self.machine.mode_protect_tools:
                self.machine.protect_tools(on=True)

            self.machine.tool = self.name
            self.installed = True
            print(f"[{self.name}] Ferramenta instalada com sucesso.")

        else:
            print(f"[{self.name}] Não é possível instalar: desinstale '{self.machine.tool}' primeiro.")

    def uninstall(self, velocity=None):
        """
        Desinstala o gripper da máquina Jubilee.

        Move o cabeçote para as coordenadas necessárias para desacoplar.
        Só executa se o gripper estiver atualmente instalado.

        Args:
            velocity (int, optional): Velocidade personalizada para o movimento.
                Se None, usa self.move_velocity.
        """
        if self.machine.tool == self.name:
            v = velocity or self.move_velocity
            self.machine.protect_tools(on=False)

            # Sequência de desacoplamento (inversa da instalação)
            self.machine.move_xyz_absolute(y=90, velocity=v)
            self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=v)
            self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=v)
            self.machine.gcode("G0 U70")
            self.machine.move_xyz_absolute(y=70, velocity=v)
            self.machine.gcode("G0 U0")

            # Reativa proteção de ferramentas
            if self.machine.mode_protect_tools:
                self.machine.protect_tools(on=True)

            self.machine.tool = None
            self.installed = False
            print(f"[{self.name}] Ferramenta desinstalada com sucesso.")

        else:
            print(f"[{self.name}] Nenhum gripper instalado ou outra ferramenta ativa.")

    # ====== Controle do Servo ======
    def set_angle(self, angle):
        """Define o ângulo do servo (0° a 180°)."""
        duty = 2.5 + (angle / 180.0) * 10.0
        lgpio.tx_pwm(self.handle, self.servo_pin, 50, duty)

    def begin(self):
        """Abre o manipulador GPIO."""
        self.handle = lgpio.gpiochip_open(0)

    def end(self):
        """Fecha o manipulador GPIO."""
        if self.handle is not None:
            lgpio.gpiochip_close(self.handle)
            self.handle = None

    def open(self):
        """Abre o gripper (ângulo padrão de 30°)."""
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(30)
        time.sleep(0.5)
        self.end()

    def open_angles(self, angle):
        """Abre o gripper em um ângulo específico."""
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(angle)
        time.sleep(0.5)
        self.end()

    def close(self):
        """Fecha completamente o gripper (0°)."""
        self.begin()
        lgpio.gpio_claim_output(self.handle, self.servo_pin)
        self.set_angle(0)
        time.sleep(0.5)
        self.end()
