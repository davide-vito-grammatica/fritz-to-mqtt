import requests
import hashlib
import json
import time
import os
import logging
import paho.mqtt.client as mqtt
import configparser

# Leggi il file di configurazione
config = configparser.ConfigParser()
config.read('config.ini')

# Funzione per ottenere il valore della configurazione
def get_config_value(key, default=None):
    return os.getenv(key, config['DEFAULT'].get(key, default))

# Configurazione del logger
LOG_FILE = get_config_value('LOG_FILE', 'app.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s', handlers=[
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler()
])


# Configurazione FritzBox dalle variabili d'ambiente
FRITZBOX_URL = get_config_value('FRITZBOX_URL', 'http://192.168.1.1')
USERNAME = get_config_value('USERNAME', 'davide')
PASSWORD = get_config_value('PASSWORD', 'dafra123')
SID_FILE = get_config_value('SID_FILE', 'sid.json')

LOOP_TIMEOUT =  int(get_config_value('LOOP_TIMEOUT', '30'))

# Configurazione MQTT dalle variabili d'ambiente
MQTT_BROKER = get_config_value('MQTT_BROKER', '192.168.1.44')
MQTT_PORT = int(get_config_value('MQTT_PORT', 1883))
MQTT_USERNAME = get_config_value('MQTT_USERNAME', 'username')
MQTT_PASSWORD = get_config_value('MQTT_PASSWORD', 'password')
MQTT_BASE_TOPIC = get_config_value('MQTT_BASE_TOPIC', 'home/fritzbox/wifi')

def check_sid_validity(sid):
    test_url = f"{FRITZBOX_URL}/data.lua"
    test_data = {
        "xhr": 1,
        "sid": sid,
        "lang": "en",
        "page": "overview"
    }
    
    response = requests.post(test_url, data=test_data)
    
    # Se il SID è ancora valido, la risposta sarà corretta
    try:
        response_json = response.json()
        sid = response_json.get("sid", "")
        return isinstance(sid, str) and len(sid) == 16 and sid.isalnum()
    except json.JSONDecodeError:
        return False

def login_fritzbox():
    login_url = f"{FRITZBOX_URL}/login_sid.lua"
    
    # Primo step: ottenere il challenge
    response = requests.get(login_url)
    challenge = response.text.split("<Challenge>")[1].split("</Challenge>")[0]
    
    # Calcolare l'hash della password
    challenge_response = f"{challenge}-{PASSWORD}".encode('utf-16le')
    hashed_response = hashlib.md5(challenge_response).hexdigest()
    
    # Effettuare il login con il response hash
    login_payload = {
        "username": USERNAME,
        "response": f"{challenge}-{hashed_response}"
    }
    login_response = requests.get(login_url, params=login_payload)
    
    # Estrarre il SID
    sid = login_response.text.split("<SID>")[1].split("</SID>")[0]
    
    # Controllo se il login è avvenuto con successo
    if sid == "0000000000000000":
        logging.error("Login fallito, verifica username e password")
        raise Exception("Login fallito, verifica username e password")
    
    # Salva il SID nel file
    with open(SID_FILE, "w") as file:
        json.dump({"sid": sid}, file)

    logging.info("Login avvenuto con successo")
    return sid

def fetch_and_publish_wifi_data():
    data_url = f"{FRITZBOX_URL}/data.lua"
    post_data = {
        "lang": "en",
        "page": "chan",
        "xhrId": "environment",
        "requestCount": 0,
        "useajax": 1,
        "no_sidrenew": "",
        "sid": get_sid()
    }

    try:
        response = requests.post(data_url, data=post_data)
        wifi_data = response.json()
        
        scanlist = wifi_data.get('data', {}).get('scanlist', [])
        
       
        # Pubblica ogni rete WiFi trovata su un topic separato
        for network in scanlist:
             # Connettere al broker MQTT
            client = mqtt.Client()
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  # Aggiunta credenziali MQTT
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            # Attendere la connessione
            client.loop_start()
            while not client.is_connected():
                time.sleep(0.1)
        
            ssid = network.get('ssid', 'unknown_ssid')
            bandid = network.get('bandId', 'unknown_bandid')
            channel = network.get('channel', 'unknown_channel')
            if not ssid or ssid == 'unknown_ssid':
                logging.warning(f"SSID non valido o sconosciuto: {network}")
                continue
            
            topic = f"{MQTT_BASE_TOPIC}/{bandid}/{channel}/{ssid}"
            structured_data = {
                "network": network,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }
            formatted_data = json.dumps(structured_data, indent=4)
            result = client.publish(topic, formatted_data, qos=1, retain=False)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Pubblicato su {topic}: {formatted_data}")
            elif result.rc == mqtt.MQTT_ERR_NO_CONN:
                logging.error(f"Errore nella pubblicazione su {topic}: Client non connesso")
            elif result.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
                logging.error(f"Errore nella pubblicazione su {topic}: Coda di messaggi piena")
            else:
                logging.error(f"Errore nella pubblicazione su {topic}: {result.rc}")
        
        client.loop_stop()
        client.disconnect()
        logging.info("Dati WiFi inviati a Home Assistant via MQTT")

    except Exception as e:
        logging.error(f"Errore nella richiesta dati: {e}")

def get_sid():
    try:
        with open(SID_FILE, "r") as file:
            data = json.load(file)
            sid = data.get("sid")
            if sid and check_sid_validity(sid):
                return sid  # Restituisce il SID se valido
    except FileNotFoundError:
        pass

    # Se non esiste o è scaduto, effettua il login
    return login_fritzbox()

# Loop per il polling continuo
if __name__ == "__main__":
    while True:
        fetch_and_publish_wifi_data()
        time.sleep(5)