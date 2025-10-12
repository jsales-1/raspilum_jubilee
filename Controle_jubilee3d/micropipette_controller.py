class Micropipette:
    """
    Classe para controle de uma micropipeta automatizada integrada
    em uma Jubilee.

    Esta versão segue a mesma lógica das outras ferramentas (ex: camera_tool, Gripper),
    incluindo controle de estado, nome, e verificação de ferramenta atual.
    """

    def __init__(self, machine, parking_position_xy=(138, 18), move_velocity=10000):
        """
        Inicializa a micropipeta e posiciona o eixo Z em uma altura segura.

        Args:
            machine: Instância de controle da máquina Jubilee.
            parking_position_xy (tuple, optional): Coordenadas (X, Y) para 
                estacionamento da micropipeta. Default é (138, 18).
            move_velocity (int, optional): Velocidade padrão de movimentação (mm/min).
        """
        self.name = "Micropipeta"
        self.parking_position_x, self.parking_position_y = parking_position_xy
        self.machine = machine
        self.move_velocity = move_velocity
        self.liquid_ul = 0
        self.installed = False

        self.machine.gcode("M208 Z100:300")
        self.machine.gcode('M98 P"/sys/homev.g"')
        if self.machine.position[2] < 100:
            self.machine.move_xyz_absolute(z=100)

    def install(self):
        """
        Instala a micropipeta na máquina Jubilee.

        Move o cabeçote até as coordenadas específicas necessárias
        para acoplar a micropipeta ao sistema.
        """
        if self.machine.tool is None:
            self.machine.protect_tools(on=False)

            self.machine.move_xyz_absolute(y=220, velocity=self.move_velocity)
            self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=self.move_velocity)
            self.machine.gcode("G0 U70")
            self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=self.move_velocity)
            self.machine.gcode("G0 U0")
            self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)

            if self.machine.mode_protect_tools:
                self.machine.protect_tools(on=True)

            self.machine.tool = self.name
            self.installed = True

        else:
            print(f"[{self.name}] Não é possível instalar: desinstale '{self.machine.tool}' primeiro.")


    def uninstall(self, velocity=None):
        """
        Desinstala a micropipeta da máquina Jubilee.

        Move o cabeçote até as coordenadas específicas necessárias
        para desacoplar a micropipeta do sistema.
        """
        if self.machine.tool == self.name:
            v = velocity or self.move_velocity
            self.machine.protect_tools(on=False)

            self.machine.move_xyz_absolute(y=90, velocity=v)
            self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=v)
            self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=v)
            self.machine.gcode("G0 U70")
            self.machine.move_xyz_absolute(y=70, velocity=v)
            self.machine.gcode("G0 U0")

            if self.machine.mode_protect_tools:
                self.machine.protect_tools(on=True)

            self.machine.tool = None
            self.installed = False
        else:
            print(f"[{self.name}] Nenhuma micropipeta instalada ou outra ferramenta ativa.")


    def press(self, ul):
        """
        Pressiona o êmbolo da micropipeta para definir o volume a ser aspirado.

        Args:
            ul (float): Volume em microlitros (µL) que se deseja aspirar.
                        O valor máximo permitido é 1200 µL.
        """
        if ul > 1200:
            print(f"[{self.name}] Não tente pipetar mais que 1200 µL.")
            return

        if self.liquid_ul > 0:
            self.machine.gcode("G0 V350")
            self.liquid_ul = 0

        next_position = round(((ul + 13.68852)/3.42413),2)
        self.machine.gcode(f"G0 V{next_position}")


    def press_step(self, give_step):
        """Pressiona o êmbolo diretamente em um valor de passo."""
        if give_step > 300:
            print(f"[{self.name}] Limite máximo de curso atingido.")
            return

        if self.liquid_ul > 0:
            self.machine.gcode("G0 V350")
            self.liquid_ul = 0

        self.machine.gcode(f"G0 V{give_step}")


    def aspirate(self):
        """
        Aspira o líquido previamente configurado pelo método `press`.

        Atualiza o atributo `liquid_ul` com o volume atualmente aspirado.
        """
        positions = self.machine.gcode("M114")
        valor_v = float(positions.split("V:")[1].split("E:")[0].strip())

        if valor_v == 0:
            print(f"[{self.name}] Use o método 'press' antes de aspirar.")
            return

        self.liquid_ul = valor_v * 3.42413 + 13.68852
        self.machine.gcode("G0 V0")


    def dispense(self):
        """
        Dispensa o líquido atualmente aspirado.
        """
        self.machine.gcode("G0 V400")
        self.liquid_ul = 0


    def eject_tip(self):
        """
        Ejeta a ponteira da micropipeta.
        """
        self.machine.gcode("G0 V450")
        self.liquid_ul = 0
        self.machine.gcode("G0 V0")
