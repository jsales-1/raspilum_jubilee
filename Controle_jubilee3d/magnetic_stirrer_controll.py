import lgpio
import time

class Agitador:
    def __init__(self, pin=6, chip=0):
        """Inicializa o agitador, configurando o pino GPIO."""
        self.pin = pin
        self.chip = chip
        self.h = lgpio.gpiochip_open(self.chip)
        lgpio.gpio_claim_output(self.h, self.pin)
        print(f"Agitador configurado no GPIO{self.pin}.")

    def ligar(self):
        """Liga o agitador."""
        lgpio.gpio_write(self.h, self.pin, 1)
        print("Agitador ligado.")

    def desligar(self):
        """Desliga o agitador."""
        lgpio.gpio_write(self.h, self.pin, 0)
        print("Agitador desligado.")

    def ativar_por(self, tempo):
        """Liga o agitador por um tempo em segundos."""
        self.ligar()
        time.sleep(tempo)
        self.desligar()

    def fechar(self):
        """Libera o acesso ao chip GPIO."""
        lgpio.gpiochip_close(self.h)
        print("Chip GPIO liberado.")
