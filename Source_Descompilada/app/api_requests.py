import requests
from unidecode import unidecode
from urllib.parse import quote
from datetime import datetime, timedelta

tempoDeRequest = 5
API_KEY = "f9db00dad919fcd40f17a81007efae15"

def buscar_cidades_estado(estado):
    try:
        url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado}/municipios'
        response = requests.get(url)
        if response.status_code == 200:
            cidades = [cidade['nome'] for cidade in response.json()]
            return cidades
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar cidades: {e}")
        return []

def graus_para_direcao(angle):
    directions = ['Norte', 'Nordeste', 'Leste', 'Sudeste', 'Sul', 'Sudoeste', 'Oeste', 'Noroeste']
    idx = int((angle + 22.5) // 45) % 8
    return directions[idx]

def buscar_clima(cidade, estado):
    try:
        cidade_tratada = unidecode(cidade.strip())
        query = quote(f"{cidade_tratada},BR")

        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        geo_resp = requests.get(geo_url, timeout=tempoDeRequest)
        if geo_resp.status_code != 200 or not geo_resp.json():
            print(f"Erro geocodificação ou cidade não encontrada: {cidade}")
            return None

        geo_data = geo_resp.json()[0]
        lat = geo_data['lat']
        lon = geo_data['lon']


        clima_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        clima_resp = requests.get(clima_url, timeout=tempoDeRequest)

        if clima_resp.status_code != 200:
            print(f"Erro ao buscar clima atual ({cidade})")
            return None

        dados_atuais = clima_resp.json()

        temp_atual = dados_atuais['main']['temp']
        descricao = dados_atuais['weather'][0]['description']
        umidade = dados_atuais['main']['humidity']
        vento = dados_atuais['wind']['speed']
        vento_graus = dados_atuais['wind'].get('deg')
        direcao_vento = graus_para_direcao(vento_graus) if vento_graus is not None else 'N/A'

        nascer_sol_ts = dados_atuais['sys'].get('sunrise')
        nascer_sol = datetime.fromtimestamp(nascer_sol_ts).strftime('%H:%M:%S') if nascer_sol_ts else 'N/A'


        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        forecast_resp = requests.get(forecast_url, timeout=tempoDeRequest)

        temp_min = None
        temp_max = None

        if forecast_resp.status_code == 200:
            dados_forecast = forecast_resp.json()
            timezone_offset = dados_forecast.get('city', {}).get('timezone', 0)  

            agora_utc = datetime.utcnow()
            agora_local = agora_utc + timedelta(seconds=timezone_offset)
            hoje = agora_local.date()

            temps_hoje = []

            for entrada in dados_forecast['list']:
                data_txt = entrada['dt_txt']
                data_utc = datetime.strptime(data_txt, "%Y-%m-%d %H:%M:%S")
                data_local = data_utc + timedelta(seconds=timezone_offset)

                if data_local.date() == hoje:
                    temps_hoje.append(entrada['main']['temp'])

            if temps_hoje:
                temp_min = round(min(temps_hoje), 1)
                temp_max = round(max(temps_hoje), 1)


        if temp_min is None or temp_max is None:
            temp_min = dados_atuais['main'].get('temp_min', temp_atual)
            temp_max = dados_atuais['main'].get('temp_max', temp_atual)

        clima = {
            'temperatura': round(temp_atual, 1),
            'temp_min': temp_min,
            'temp_max': temp_max,
            'descricao': descricao,
            'umidade': umidade,
            'vento': vento,
            'vento_direcao': direcao_vento,
            'nascer_sol': nascer_sol,
        }
        return clima

    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao buscar clima: {e}")
        return None
