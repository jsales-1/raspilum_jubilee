class Micropipette: 
    """
    Classe para controle de uma micropipeta automatizada integrada
    em uma Jubilee.

    Esta classe simula o funcionamento de uma pipeta de deslocamento
    positivo, permitindo instalar/desinstalar a ferramenta e realizar
    operações de pipetagem como aspirar, dispensar e ejetar ponteiras.

    Attributes:
        machine: Objeto que representa a máquina Jubilee, permitindo
            enviar comandos G-Code e realizar movimentações.
        parking_position_x (float): Posição X de estacionamento/acoplamento.
        parking_position_y (float): Posição Y de estacionamento/acoplamento.
        move_velocity (int): Velocidade dos movimentos em mm/min.
        liquid_ul (float): Volume de líquido atualmente aspirado, em microlitros (µL).
    """

    def __init__(self, machine, parking_position_xy=(138, 18)):
        """
        Inicializa a micropipeta e posiciona o eixo Z em uma altura segura.

        Args:
            machine: Instância de controle da máquina Jubilee.
            parking_position_xy (tuple, optional): Coordenadas (X, Y) para 
                estacionamento da micropipeta. Default é (138, 18).
        """
        self.parking_position_x, self.parking_position_y = parking_position_xy
        self.machine = machine
        self.move_velocity = 10000

        # Altura mínima de segurança no eixo Z e homing
        self.machine.gcode("M208 Z100:300")
        self.machine.gcode('M98 P"/sys/homev.g"')
        if self.machine.position[2] < 100:
            self.machine.move_xyz_absolute(z=100)
        
        self.liquid_ul = 0

    def install(self):
        """
        Instala a micropipeta na máquina Jubilee.

        Move o cabeçote até as coordenadas específicas necessárias
        para acoplar a micropipeta ao sistema.
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
        Desinstala a micropipeta da máquina Jubilee.

        Move o cabeçote até as coordenadas específicas necessárias
        para desacoplar a micropipeta do sistema.
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

    def press(self, ul):
        """
        Pressiona o êmbolo da micropipeta para definir o volume a ser aspirado.

        Args:
            ul (float): Volume em microlitros (µL) que se deseja aspirar.
                        O valor máximo permitido é 1200 µL.

        Observações:
            - Caso já haja líquido armazenado (`liquid_ul > 0`), 
              o êmbolo é zerado antes de um novo ajuste.
            - O movimento do êmbolo é controlado pelo eixo virtual V
              do firmware da máquina.
        """
        if ul > 1200:
            print("Não tente pipetar mais que 1200 µL")
            return

        if self.liquid_ul > 0:
            self.machine.gcode("G0 V350")
            self.liquid_ul = 0
        
        next_position = ul / 4
        self.machine.gcode(f"G0 V{next_position}")
    

    def press_step(self, give_step):

        if give_step > 300:
            print("Não tente pipetar mais que 1200 µL")
            return

        if self.liquid_ul > 0:
            self.machine.gcode("G0 V350")
            self.liquid_ul = 0
        
        self.machine.gcode(f"G0 V{give_step}")

    def aspirate(self):
        """
        Aspira o líquido previamente configurado pelo método `press`.

        Atualiza o atributo `liquid_ul` com o volume atualmente aspirado.

        Observações:
            - É necessário usar o método `press` antes, para definir
              o volume desejado.
            - O valor do eixo V é convertido em microlitros usando a 
              relação: `liquid_ul = V * 4`.
        """
        positions = self.machine.gcode("M114")
        valor_v = float(positions.split("V:")[1].split("E:")[0].strip())
        if valor_v == 0:
            print("Use o método 'press' antes")
            return
        
        self.liquid_ul = valor_v * 4
        self.machine.gcode("G0 V0")

    def dispense(self):
        """
        Dispensa o líquido atualmente aspirado.

        Move o êmbolo da micropipeta até a posição V=400,
        liberando o conteúdo e zerando `liquid_ul`.
        """
        self.machine.gcode("G0 V400")
        self.liquid_ul = 0

    def eject_tip(self):
        """
        Ejeta a ponteira da micropipeta.

        Move o êmbolo até V=450 para ejetar a ponteira usada e 
        retorna em seguida para V=0, garantindo que a micropipeta 
        esteja pronta para receber uma nova ponteira.
        """
        self.machine.gcode("G0 V450")
        self.liquid_ul = 0
        self.machine.gcode("G0 V0")
