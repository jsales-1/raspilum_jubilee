class Micropipette:
    """
    Classe para controle de uma micropipeta automatizada integrada
    em uma Jubilee.

    Esta versão segue a mesma lógica das outras ferramentas (ex: camera_tool, Gripper),
    incluindo controle de estado, nome, e verificação de ferramenta atual.
    """

    def __init__(self, machine, parking_position_xy=(138, 16), move_velocity=3000,linear_coeficientes_ab=(3.49009,12.82974)):
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
        self.linear_coeficientes_ab=linear_coeficientes_ab
        self.liquid_ul = 0
        self.installed = False
        self.tip = False
        self.machine.gcode('M98 P"/sys/homev.g"')


    def install(self):
        """
        Instala a micropipeta na máquina Jubilee.

        Move o cabeçote até as coordenadas específicas necessárias
        para acoplar a micropipeta ao sistema.
        """
    
        if self.machine.tool is None:
            if self.tip:
                self.machine.gcode("M208 Z160:300")
            else:
                self.machine.gcode("M208 Z150:300")
            

            if self.machine.position[2] < 150:
                self.machine.move_xyz_absolute(z=150)
            self.machine.protect_tools(on=False)

            self.machine.move_xyz_absolute(y=220, velocity=self.move_velocity)
            self.machine.move_xyz_absolute(x=self.parking_position_x, velocity=self.move_velocity)
            self.machine.gcode("G91 G1 U10 F600 G90")  
            self.machine.gcode("G91 G1 H1 U300 F3000 G90")  
            self.machine.move_xyz_absolute(y=self.parking_position_y, velocity=self.move_velocity)
            self.machine.gcode("G92 U20")  
            self.machine.gcode("G91 G1 U-10 F600 G90")  
            self.machine.gcode("G91 G1 H1 U-300 F3000 G90")
            self.machine.gcode("G92 U0") 
            self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)

            if self.machine.mode_protect_tools:
                self.machine.protect_tools(on=True,min_xy=[20,90])
                self.machine.gcode("M208 Z150:320")

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
            self.machine.gcode("G91 G1 U10 F600 G90")  
            self.machine.gcode("G91 G1 H1 U300 F3000 G90")  
            self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
            self.machine.move_xyz_absolute(x=50, y=120, velocity=self.move_velocity)
            self.machine.gcode("G92 U20")  
            self.machine.gcode("G91 G1 U-10 F600 G90")  
            self.machine.gcode("G91 G1 H1 U-300 F3000 G90")
            self.machine.gcode("G92 U0") 

            if self.machine.mode_protect_tools:
                self.machine.protect_tools(on=True)

            self.machine.tool = None
            self.installed = False
            self.machine.gcode("M208 Z0:320")

        else:
            print(f"[{self.name}] Nenhuma micropipeta instalada ou outra ferramenta ativa.")


    def press(self, ul):
        """
        Pressiona o êmbolo da micropipeta para definir o volume a ser aspirado.

        Args:
            ul (float): Volume em microlitros (µL) que se deseja aspirar.
                        O valor máximo permitido é 1200 µL.
        """
        if self.tip:
            if ul > 1200:
                print(f"[{self.name}] Não tente pipetar mais que 1200 µL.")
                return

            if self.liquid_ul > 0:
                self.machine.gcode("G0 V350 F10000")
                self.liquid_ul = 0

            next_position = round(((ul + self.linear_coeficientes_ab[1])/self.linear_coeficientes_ab[0]),2)
            self.machine.gcode(f"G0 V{next_position} F10000")

        else:
            print("Acople a ponteira")


    def press_step(self, give_step):
        """Pressiona o êmbolo diretamente em um valor de passo."""
        if give_step > 300:
            print(f"[{self.name}] Limite máximo de curso atingido.")
            return

        if self.liquid_ul > 0:
            self.machine.gcode("G0 V350 F1200")
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

        self.liquid_ul = valor_v * self.linear_coeficientes_ab[0] + self.linear_coeficientes_ab[1]
        self.machine.gcode("G0 V0 F4000")


    def dispense(self,velocity=None):
        """
        Dispensa o líquido atualmente aspirado.
        """
        if velocity == None:
            self.machine.gcode("G0 V352 F800")
        else:
            velocidade_step_min=(velocity * 60) / self.linear_coeficientes_ab[0]
            self.machine.gcode(f"G0 V352 F{int(velocidade_step_min)}")
            
        self.liquid_ul = 0
        self.machine.gcode("G0 V175 F10000")


    def eject_tip(self,velocity=9000):
        """
        Ejeta a ponteira da micropipeta.
        """
        self.machine.gcode(f"G0 V450 F{velocity}")
        self.liquid_ul = 0
        self.machine.gcode(f"G0 V0 F{velocity}")
        self.tip = False
        self.machine.gcode("M208 Z150:320")


    def attach_tip(self,tip_box_position,safe_height=320,move_velocity=3000):
        self.machine.move_xyz_absolute(z=safe_height,velocity=1800)
        self.machine.move_xyz_absolute(tip_box_position[0], tip_box_position[1], velocity=move_velocity)
        self.machine.move_xyz_absolute(z=tip_box_position[2], velocity=500)
        self.machine.move_xyz_absolute(z=safe_height)
        tip_box_position[0] -= 10
        self.tip = True
        self.machine.gcode("M208 Z160:320")
        

    def discart_tip(self,discart_position:list,safe_height=320,move_velocity=3000):
        self.machine.move_xyz_absolute(z=safe_height,velocity=1600)
        self.machine.move_xyz_absolute(discart_position[0], discart_position[1], velocity=move_velocity)
        self.machine.move_xyz_absolute(z=discart_position[2], velocity=1000)
        self.eject_tip()

    
    def pipette_liquid(self,start_position_xyz, end_position, volume_ul, safe_height = 320, velocidade_dispensacao=300, move_velocity=3000):
        ciclos = int(volume_ul // 1000)
        remaining = volume_ul % 1000

        if self.tip:

            def transfer(volume):
                self.machine.move_xyz_absolute(z=safe_height,velocity=1600)
                self.press(volume)
                self.machine.move_xyz_absolute(start_position_xyz[0], start_position_xyz[1], velocity=move_velocity)
                self.machine.move_xyz_absolute(z=start_position_xyz[2], velocity=600)
                self.aspirate()
                self.machine.move_xyz_absolute(z=safe_height)
                self.machine.move_xyz_absolute(end_position[0], end_position[1], velocity=move_velocity)
                self.machine.move_xyz_absolute(z=end_position[2],velocity=600)
                self.dispense(velocity=velocidade_dispensacao)
                self.machine.move_xyz_absolute(z=safe_height,velocity=1600)

            for _ in range(ciclos):
                transfer(1000)

            if remaining > 0:
                transfer(remaining)
        
        else:
            print("Acople uma ponteira antes")