from datetime import datetime
import pandas as pd
import board
import adafruit_dht
import lgpio
import time


h = lgpio.gpiochip_open(0)


dhtDevice = adafruit_dht.DHT11(board.D26)


n = 1000

dados = {
    'Temperatura (°C)':[],
    'Umidade (%)':[],
    'Hora':[]
}

for i in range(n):

    now = datetime.now()

    current_time_hms = now.strftime("%D  %H:%M:%S")

    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        dados['Temperatura (°C)'].append(temperature_c)
        dados['Umidade (%)'].append(humidity)
        dados['Hora'].append(current_time_hms)

        

    except:
        continue
            

    df = pd.DataFrame(dados)
    df.to_excel("analise2.xlsx")
    
    time.sleep(1830)