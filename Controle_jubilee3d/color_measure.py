import lgpio
import time


class GY31:
    def __init__(self, gpio_out=17, s2=27, s3=22, chip=0):
        self.GPIO_OUT = gpio_out
        self.S2 = s2
        self.S3 = s3

        self.h = lgpio.gpiochip_open(chip)

        lgpio.gpio_claim_output(self.h, self.S2)
        lgpio.gpio_claim_output(self.h, self.S3)
        lgpio.gpio_claim_input(self.h, self.GPIO_OUT)

        self._pulse_count = 0

        self._cb = lgpio.callback(
            self.h,
            self.GPIO_OUT,
            lgpio.RISING_EDGE,
            self._pulse_callback
        )

    def _pulse_callback(self, chip, gpio, level, tick):
        self._pulse_count += 1

    def _set_filter(self, s2, s3):
        lgpio.gpio_write(self.h, self.S2, s2)
        lgpio.gpio_write(self.h, self.S3, s3)
        time.sleep(0.01)

    def _measure_frequency(self, duration=0.1):
        self._pulse_count = 0
        start = time.time()

        time.sleep(duration)

        elapsed = time.time() - start
        return self._pulse_count / elapsed

    def read_color(self, color):
        if color == "red":
            self._set_filter(0, 0)
        elif color == "blue":
            self._set_filter(0, 1)
        elif color == "green":
            self._set_filter(1, 1)
        else:
            raise ValueError("Cor inválida")

        return self._measure_frequency()

    def read_rgb(self):
        return {
            "red": self.read_color("red"),
            "green": self.read_color("green"),
            "blue": self.read_color("blue")
        }

    def save_samples_to_file(self, filename, n=10, interval=0.02):
        """
        Faz N leituras e salva no arquivo TXT

        filename: nome do arquivo (ex: 'dados.txt')
        n: número de amostras
        interval: tempo entre leituras
        """

        with open(filename, "w") as f:
            f.write("index,red,green,blue\n")

            for i in range(n):
                rgb = self.read_rgb()

                line = f"{i},{rgb['red']:.2f},{rgb['green']:.2f},{rgb['blue']:.2f}\n"
                f.write(line)

                time.sleep(interval)

        print(f"Arquivo '{filename}' salvo com {n} leituras.")

    def close(self):
        self._cb.cancel()
        lgpio.gpiochip_close(self.h)