import cv2
import numpy as np


class camera_tool:
    """ Classe para controle de uma ferramenta de câmera em um sistema Jubilee ou similar.

    Esta classe encapsula os comandos necessários para instalar, desinstalar
    e capturar imagens usando uma câmera acoplada à máquina. A movimentação
    é feita através da interface da máquina, enquanto a captura de imagens
    utiliza a biblioteca OpenCV.

    Atributos da classe
    ----------
    installed : bool
        Indica se a câmera está instalada no sistema.
    machine : objeto
        Interface da máquina controlada (deve implementar métodos como `move_xyz_absolute` e `gcode`).
    move_velocity : int
        Velocidade padrão para movimentação do cabeçote durante instalação/desinstalação."""

    def __init__(self, machine):
        """
        Inicializa a ferramenta da câmera.

        Parâmetros
        ----------
        machine : Instância da Jubilee.
        """
        self.installed = False
        self.machine = machine
        self.move_velocity = 10000

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
        self.machine.move_xyz_absolute(x=302, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=7, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=50, y=120, velocity=self.move_velocity)

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
        self.machine.move_xyz_absolute(x=302, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(y=7, velocity=self.move_velocity)
        self.machine.gcode("G0 U70")
        self.machine.move_xyz_absolute(y=70, velocity=self.move_velocity)
        self.machine.move_xyz_absolute(x=50, y=120, velocity=self.move_velocity)
        self.machine.gcode("G0 U0")

        if self.machine.mode_protect_tools:
            self.machine.protect_tools(on=False)

    def photo(self, filename='captura.jpg', video_index=0):
        """
        Captura uma imagem usando a câmera conectada.

        Este método abre um dispositivo de captura de vídeo via OpenCV,
        obtém um frame e salva como arquivo de imagem.

        Parâmetros
        ----------
        filename : str, opcional
            Nome do arquivo de saída da imagem capturada (padrão: 'captura.jpg').
        video_index : int, opcional
            Índice do dispositivo de captura de vídeo (padrão: 0).

        Retorna
        -------
        None
            Não há retorno. Se a captura falhar, o método apenas encerra silenciosamente.
        """
        cap = cv2.VideoCapture(video_index)
        if not cap.isOpened():
            return

        ret, frame = cap.read()
        if not ret:
            cap.release()
            return

        cv2.imwrite(filename, frame)
        cap.release()
