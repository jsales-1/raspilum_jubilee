"""Driver para controlar a Jubilee"""

import requests 
import json
import time
import curses
import pprint
from inpromptu import Inpromptu
from functools import wraps
from pynput import keyboard


class MachineStateError(Exception):
    """Erro lançado se a máquina estiver em estado incorreto para executar o comando."""
    pass

def machine_is_homed(func):
    """Decorador que verifica se a máquina está referenciada antes de executar um comando."""
    @wraps(func)
    def homing_check(self, *args, **kwds):
        """Verifica o valor em cache dos eixos; consulta o estado se necessário."""
        if self.axes_homed and all(self.axes_homed):
            return func(self, *args, **kwds)
        self.axes_homed = json.loads(self.gcode("M409 K\"move.axes[].homed\""))["result"][:4]
        if not all(self.axes_homed):
            raise MachineStateError("Erro: a máquina deve estar referenciada primeiro.")
        return func(self, *args, **kwds)
    return homing_check


class JubileeMotionController(Inpromptu):
    """Driver para enviar comandos de movimento e consultar o estado da máquina."""

    LOCALHOST = "127.0.0.1"

    def __init__(self, address=LOCALHOST, debug=False, simulated=False, reset=False):
        """Inicializa conexões, estado da máquina e configurações padrão."""
        if address != self.__class__.LOCALHOST:
            print("Aviso: desconectar este aplicativo da rede encerrará a conexão com a Jubilee.")
        self.address = address
        self.debug = debug
        self.simulated = simulated
        self.model_update_timestamp = 0
        self.command_ws = None
        self.wake_time = None
        self.absolute_moves = True
        self.tool = None
        #self._active_tool_index = None
        #self._tool_z_offsets = None
        self._axis_limits = None
        self.connect()
        self.axes_homed = [False]*4
        if reset:
            self.reset()
        self._set_absolute_moves(force=True)
        self.mode_protect_tools = False
        self.gcode('M98 P"/sys/config.g"')


    def connect(self):
        """Conecta à Jubilee via HTTP e inicializa caches de propriedades."""
        if self.simulated:
            return
        if self.debug:
            print(f"Conectando a {self.address} ...")
        try:
            # Consulta o estado dos eixos como um 'ping' à máquina.
            self.axes_homed = json.loads(self.gcode("M409 K\"move.axes[].homed\"", timeout=1))["result"][:4]

            # Zera caches de propriedades que dependem da conexão.
            self._active_tool_index = None
            self._tool_z_offsets = None
            self._axis_limits = None

            # Atualiza propriedades importantes na primeira conexão para agilizar o acesso.
            self.active_tool_index
            self.tool_z_offsets
            self.axis_limits

            # Define movimentos absolutos.
            self._set_absolute_moves(force=True)
        except json.decoder.JSONDecodeError as e:
            raise MachineStateError("DCS não está pronto para conectar.") from e
        except requests.exceptions.Timeout as e:
            raise MachineStateError("Tempo de conexão esgotado. URL inválida ou máquina não conectada.") from e
        if self.debug:
            print("Conectado.")


    def gcode(self, cmd: str = "", timeout: float = None):
        """Envia um comando GCode e retorna a resposta."""
        if self.debug or self.simulated:
            print(f"enviando: {cmd}")
        if self.simulated:
            return None

        response = requests.post(f"http://{self.address}/machine/code", data=f"{cmd}", timeout=timeout).text
        if self.debug:
            print(f"recebido: {response}")
        return response


    def download_file(self, filepath: str = None, timeout: float = None):
        """Baixa um arquivo da máquina especificando o caminho completo. Ex.: /sys/tfree0.g."""
        file_contents = requests.get(f"http://{self.address}/machine/file{filepath}",
                                    timeout=timeout).text
        return file_contents


    def reset(self):
        """Executa um reset de software e tenta reconectar a máquina."""
        self.gcode("M999")  # Reseta a placa; assume que já está conectado
        self.axes_homed = [False]*4
        self.disconnect()
        print("Reconectando...")
        for i in range(10):
            time.sleep(1)
            try:
                self.connect()
                self.axes_homed = [False]*4
                return
            except MachineStateError:
                pass
        raise MachineStateError("Falha ao reconectar.")


    def home_all_forced(self):
        """Força todos os eixos como referenciados (X, Y, Z, U)."""
        self.axes_homed = [True, True, True, True]
        all_axis = ["X","Y","Z","U"]
        for i,axi in zip(self.position,all_axis):
            self.gcode(f"G92 {axi}{i}")


    def home_all(self, mesh_mode_z=True):
        """Referencia todos os eixos da máquina."""
        self.home_xy()
        self.home_z(mesh_mode_z)
        self.home_u()


    def home_xy(self):
        """Referencia os eixos XY.
        Y é referenciado antes de X para evitar colisão com o suporte de ferramentas.
        """
        self.gcode('M98 P"/sys/homey.g"')
        self.gcode('M98 P"/sys/homex.g"')
        self.axes_homed[0] = True
        self.axes_homed[1] = True


    def home_z(self, mesh_mode=True):
        """Referencia o eixo Z.
        A base deve estar livre de obstáculos antes de executar.
        """
        response = input("A base está livre de obstáculos? [s/n]")
        if response.lower() in ["s", "sim"]:
            if mesh_mode:
                self.gcode('M98 P"/sys/homez.g"')
            else:
                self.gcode('M98 P"/sys/homez_NM.g"')
        self.axes_homed[2] = True


    def home_u(self):
        """Referencia o eixo U.
        A base deve estar livre de obstáculos antes de executar.
        """
        response = input("A base está livre de obstáculos? [s/n]")
        if response.lower() in ["s", "sim"]:
            self.gcode('M98 P"/sys/homeu.g"')
        self.axes_homed[3] = True


    def protect_tools(self, on: bool):
        """Ativa ou desativa a proteção das ferramentas."""
        if on:
            self.gcode("M208 Y50:400")
            self.mode_protect_tools = True
        else:
            self.gcode("M208 Y0:400")


    def home_in_place(self, *args: str):
        """Define a posição atual dos eixos especificados como zero."""
        for axis in args:
            if axis.upper() not in ['X', 'Y', 'Z', 'U']:
                raise TypeError(f"Erro: eixo desconhecido: {axis}.")
            self.gcode(f"G92 {axis.upper()}0")


    def turn_off_drivers(self):
        """Desliga todos os drivers da máquina."""
        self.gcode('M18')


    @machine_is_homed
    def _move_xyz(self, x: float = None, y: float = None, z: float = None, wait: bool = False, velocity:int = 13000):
        """Move a máquina nos eixos XYZ. Absoluto ou relativo definido externamente. Aguarda término se wait=True."""
        x_movement = f"X{x} " if x is not None else ""
        y_movement = f"Y{y} " if y is not None else ""
        z_movement = f"Z{z} " if z is not None else ""
        if x_movement or y_movement or z_movement:
            self.gcode(f"G0 {x_movement}{y_movement}{z_movement}F{velocity}")
        if wait:
            self.gcode(f"M400")


    def _set_absolute_moves(self, force: bool = False):
        """Define os movimentos da máquina como absolutos."""
        if self.absolute_moves and not force:
            return
        self.gcode("G90")
        self.absolute_moves = True


    def _set_relative_moves(self, force: bool = False):
        """Define os movimentos da máquina como relativos."""
        if not self.absolute_moves and not force:
            return
        self.gcode("G91")
        self.absolute_moves = False


    def emergence_stop(self):
        """Executa parada de emergência da máquina."""
        self.gcode("M112")


    def stop(self):
        """Para a execução da máquina."""
        self.gcode("M0")


    def stop_drivers(self, drivers_list: list):
        """Desliga drivers específicos ou todos se a lista estiver vazia."""
        for driver in drivers_list:
            self.gcode(f"M18 {driver}")
        if len(drivers_list) == 0:
            self.gcode("M18")


    def move_xyz_relative(self, x: float = None, y: float = None, z: float = None, wait: bool = False):
        """Move a máquina nos eixos XYZ de forma relativa."""
        self._set_relative_moves()
        self._move_xyz(x, y, z, wait)


    def move_xyz_absolute(self, x: float = None, y: float = None, z: float = None, wait: bool = False, velocity:int = 13000):
        """Move a máquina nos eixos XYZ de forma absoluta."""
        self._set_absolute_moves()
        self._move_xyz(x, y, z, wait, velocity)


    def set_feedrate(self, mm_per_min):
        """Define a velocidade de deslocamento em mm/min."""
        self.gcode(f"F{mm_per_min}")


    @property
    def position(self):
        """Retorna a posição atual do ponto de controle da máquina em mm nos eixos XYZ."""
        response_chunks = self.gcode("M114").split()
        positions = [float(a.split(":")[1]) for a in response_chunks[:3]]
        return positions


    #def pickup_tool(self, tool_index: int):
    #    """Seleciona a ferramenta especificada pelo índice."""
    #    if tool_index < 0:
    #        return
    #    self.gcode(f"T{tool_index}")
    #    self._active_tool_index = tool_index


    #def park_tool(self):
    #    """Retorna a ferramenta atual para o estacionamento."""
    #    self.gcode("T-1")
    #   self._active_tool_index = -1


    @property
    def active_tool_index(self):
        """Retorna o índice da ferramenta atualmente ativa."""
        if self._active_tool_index is None:
            try:
                response = self.gcode("T")
                if response.startswith('No tool'):
                    return -1
                elif response.startswith('Tool'):
                    self._active_tool_index = int(response.split()[1])
                else:
                    self._active_tool_index = int(response)
            except ValueError as e:
                print("Erro ao ler a ferramenta atual!")
                raise e
        return self._active_tool_index


    @property
    def tool_z_offsets(self):
        """Retorna uma lista com os offsets Z de todas as ferramentas."""
        if self._tool_z_offsets is None:
            try:
                response = json.loads(self.gcode("M409 K\"tools\""))["result"]
                self._tool_z_offsets = []
                for tool_data in response:
                    tool_z_offset = tool_data["offsets"][2]
                    self._tool_z_offsets.append(tool_z_offset)
            except ValueError as e:
                print("Erro ao ler offsets Z das ferramentas!")
                raise e
        return self._tool_z_offsets


    @property
    def axis_limits(self):
        """Retorna uma lista de tuplas (min, max) com os limites dos eixos XYZU."""
        if self._axis_limits is None:
            try:
                response = json.loads(self.gcode("M409 K\"move.axes\""))["result"]
                self._axis_limits = []
                for axis_data in response:
                    axis_min = axis_data["min"]
                    axis_max = axis_data["max"]
                    self._axis_limits.append((axis_min, axis_max))
            except ValueError as e:
                print("Erro ao ler limites dos eixos!")
                raise e
        return self._axis_limits


    @machine_is_homed
    def keyboard_controll(self):
        """Controla a máquina via teclado, movendo XYZ e ajustando passo em mm."""
        step = 10
        pressed_keys = set()
        running = True

        def on_press(key):
            nonlocal running, step
            try:
                if key.char in ['+', '-']:
                    pressed_keys.add(key.char)
            except AttributeError:
                if key in [
                    keyboard.Key.up,
                    keyboard.Key.down,
                    keyboard.Key.left,
                    keyboard.Key.right,
                    keyboard.Key.page_up,
                    keyboard.Key.page_down
                ]:
                    pressed_keys.add(key)
                elif key == keyboard.Key.esc:
                    running = False

        def on_release(key):
            try:
                if key in pressed_keys:
                    pressed_keys.remove(key)
                elif hasattr(key, "char") and key.char in pressed_keys:
                    pressed_keys.remove(key.char)
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        try:
            while running:
                if keyboard.Key.up in pressed_keys:
                    self.move_xyz_relative(0, step, 0)
                elif keyboard.Key.down in pressed_keys:
                    self.move_xyz_relative(0, -step, 0)
                elif keyboard.Key.left in pressed_keys:
                    self.move_xyz_relative(-step, 0, 0)
                elif keyboard.Key.right in pressed_keys:
                    self.move_xyz_relative(step, 0, 0)
                elif keyboard.Key.page_up in pressed_keys:
                    self.move_xyz_relative(0, 0, -step)
                elif keyboard.Key.page_down in pressed_keys:
                    self.move_xyz_relative(0, 0, step)
                elif '+' in pressed_keys:
                    step += 1
                elif '-' in pressed_keys:
                    step -= 1
                    if step < 1:
                        step = 1

                time.sleep(0.005)
                print(
                    f"X: {self.position[0]:>7.2f} | "
                    f"Y: {self.position[1]:>7.2f} | "
                    f"Z: {self.position[2]:>7.2f} || "
                    f"Passo: {step:<3} mm",
                    end="\r"
                )
        except KeyboardInterrupt:
            print("\nInterrompido")

        listener.stop()


    def disconnect(self):
        """Encerra a conexão com a máquina."""
        pass


    def __enter__(self):
        """Permite uso com contexto 'with'."""
        return self


    def __exit__(self, *args):
        """Encerra a conexão ao sair do contexto 'with'."""
        self.disconnect()
