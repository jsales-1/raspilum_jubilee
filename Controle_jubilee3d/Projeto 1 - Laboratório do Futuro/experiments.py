import time
import threading
import sys
import os
sys.path.append(os.path.abspath(".."))

from jubilee_controller import JubileeMotionController
from micropipette_controller import Micropipette
from magnetic_stirrer_controll import Agitador

from config import (
    POSICAO_BEQUER_FENOLFTALEINA,
    POSICAO_BEQUER_ACIDO,
    POSICAO_BEQUER_BASE,
    POSICAO_BEQUER_AGUA_COLETA,
    POSICAO_BEQUER_AGUA_SEGURA,
    ALTURA_SEGURA,
    VOLUME_ACIDO,
    VOLUME_BASICO,
    VOLUME_AGUA,
    VEL_DISPENSACAO,
    VEL_DISPENSACAO_AGUA,
    MOV_VELOCITY,
    TEMPO_AQUECIMENTO,
    TEMPO_AGITACAO,
    AGITADOR_PIN_1,
    AGITADOR_PIN_2,
    PIPETA_PARKING_POSITION,
    PIPETA_MOVE_VELOCITY,
)


class RaspilumController:

    def __init__(self):

        print("Inicializando Jubilee...")

        self.jubilee = JubileeMotionController()

        self.jubilee.home_all(mesh_mode_z=False)
        self.jubilee.protect_tools(on=True)
        self.jubilee.move_xyz_absolute(z=100)

        print("Inicializando micropipeta...")

        self.pipeta = Micropipette(
            self.jubilee,
            parking_position_xy=PIPETA_PARKING_POSITION,
            move_velocity=PIPETA_MOVE_VELOCITY
        )

        self.pipeta.tip = True

        print("Raspilum inicializada.")


    def experimento_fenolftaleina(self):

        print("Iniciando experimento: Fenolftaleína")

        pipeta = self.pipeta
        jubilee = self.jubilee

        agitador = Agitador(
            AGITADOR_PIN_1,
            AGITADOR_PIN_2
        )

        try:

            pipeta.install()

            jubilee.protect_tools(True)
            jubilee.move_xyz_absolute(z=300)

            agitador.ligar()

            # Ácido → Fenolftaleína
            pipeta.pipette_liquid(
                start_position_xyz=POSICAO_BEQUER_ACIDO,
                end_position=POSICAO_BEQUER_FENOLFTALEINA,
                volume_ul=VOLUME_ACIDO,
                safe_height=ALTURA_SEGURA,
                velocidade_dispensacao=VEL_DISPENSACAO,
                move_velocity=MOV_VELOCITY
            )

            # Água → posição segura
            pipeta.pipette_liquid(
                start_position_xyz=POSICAO_BEQUER_AGUA_COLETA,
                end_position=POSICAO_BEQUER_AGUA_SEGURA,
                volume_ul=VOLUME_AGUA,
                safe_height=ALTURA_SEGURA,
                velocidade_dispensacao=VEL_DISPENSACAO_AGUA,
                move_velocity=MOV_VELOCITY
            )

            # Base → Fenolftaleína
            pipeta.pipette_liquid(
                start_position_xyz=POSICAO_BEQUER_BASE,
                end_position=POSICAO_BEQUER_FENOLFTALEINA,
                volume_ul=VOLUME_BASICO,
                safe_height=ALTURA_SEGURA,
                velocidade_dispensacao=VEL_DISPENSACAO,
                move_velocity=MOV_VELOCITY
            )

            # Água → posição segura
            pipeta.pipette_liquid(
                start_position_xyz=POSICAO_BEQUER_AGUA_COLETA,
                end_position=POSICAO_BEQUER_AGUA_SEGURA,
                volume_ul=VOLUME_AGUA,
                safe_height=ALTURA_SEGURA,
                velocidade_dispensacao=VEL_DISPENSACAO_AGUA,
                move_velocity=MOV_VELOCITY
            )

            print("Experimento de Fenolftaleína concluído.")

        finally:

            # Garantir que o agitador seja desligado
            try:
                agitador.desligar()
            except Exception as e:
                print(f"Erro ao desligar agitador: {e}")

            # Garantir que a pipeta seja removida
            try:
                pipeta.uninstall()
            except Exception as e:
                print(f"Erro ao desinstalar pipeta: {e}")

            try:
                agitador.fechar()
            except Exception as e:
                print(f"Erro ao fechar agitador: {e}")


    def experimento_azul_de_metileno(self):

        print("Iniciando experimento: Azul de Metileno")

        agitador = Agitador(
            AGITADOR_PIN_1,
            AGITADOR_PIN_2
        )

        try:

            agitador.ligar()

            time.sleep(TEMPO_AGITACAO)

            agitador.desligar()

            print("Experimento de Azul de Metileno concluído.")

        finally:

            try:
                agitador.desligar()
            except Exception:
                pass

            try:
                agitador.fechar()
            except Exception:
                pass


    def experimento_cloreto(self):

        print("Iniciando experimento: Cloreto")

        agitador = Agitador(
            AGITADOR_PIN_1,
            AGITADOR_PIN_2
        )

        try:

            agitador.ligar()

            time.sleep(TEMPO_AQUECIMENTO)

            agitador.desligar()

            print("Experimento de Cloreto concluído.")

        finally:

            try:
                agitador.desligar()
            except Exception:
                pass

            try:
                agitador.fechar()
            except Exception:
                pass