import lgpio
import time

#roxo s3
class GY31:
    def __init__(self, s2=20, s3=21, out=16):
        self.S2 = s2
        self.S3 = s3
        self.OUT = out

        # abre gpiochip
        self.h = lgpio.gpiochip_open(0)

        # configura GPIO
        lgpio.gpio_claim_output(self.h, self.S2)
        lgpio.gpio_claim_output(self.h, self.S3)
        lgpio.gpio_claim_input(self.h, self.OUT)

    def _read_frequency(self, duration=0.1):
        start = time.time()
        count = 0

        last = lgpio.gpio_read(self.h, self.OUT)

        while time.time() - start < duration:
            current = lgpio.gpio_read(self.h, self.OUT)

            # borda de descida
            if last == 1 and current == 0:
                count += 1

            last = current

        return count

    def read_color(self):
        # RED
        lgpio.gpio_write(self.h, self.S2, 0)
        lgpio.gpio_write(self.h, self.S3, 0)
        time.sleep(0.02)
        red = self._read_frequency()

        # BLUE
        lgpio.gpio_write(self.h, self.S2, 0)
        lgpio.gpio_write(self.h, self.S3, 1)
        time.sleep(0.02)
        blue = self._read_frequency()

        # GREEN
        lgpio.gpio_write(self.h, self.S2, 1)
        lgpio.gpio_write(self.h, self.S3, 1)
        time.sleep(0.02)
        green = self._read_frequency()

        return {
            "red": red,
            "green": green,
            "blue": blue
        }

    def save_readings(
        self,
        filename="leituras.txt",
        n=100,
        interval=0.05
    ):
        """
        Faz N leituras e salva em TXT
        """

        with open(filename, "w") as f:

            # cabeçalho
            f.write("timestamp,red,green,blue\n")

            for i in range(n):

                data = self.read_color()

                timestamp = time.time()

                line = (
                    f"{timestamp},"
                    f"{data['red']},"
                    f"{data['green']},"
                    f"{data['blue']}\n"
                )

                f.write(line)

                print(
                    f"[{i+1}/{n}] "
                    f"R={data['red']} "
                    f"G={data['green']} "
                    f"B={data['blue']}"
                )

                time.sleep(interval)

    def close(self):
        lgpio.gpiochip_close(self.h)