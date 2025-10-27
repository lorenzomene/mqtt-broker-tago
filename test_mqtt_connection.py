
import ssl
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import time

load_dotenv()

def test_connection():
    """Testa conexão MQTT com diagnóstico detalhado"""
    host = os.getenv('TAGO_MQTT_HOST', 'mqtt.tago.io')
    port = int(os.getenv('TAGO_MQTT_PORT', '8883'))
    username = os.getenv('TAGO_MQTT_USERNAME')
    password = os.getenv('TAGO_MQTT_PASSWORD')
    device_id = os.getenv('DEVICE_ID', 'device_001')
    
    print("=" * 60)
    print("DIAGNOSTICO DE CONEXAO MQTT - TAGO.IO")
    print("=" * 60)
    
    print(f"Host: {host}")
    print(f"Porta: {port}")
    print(f"Device ID: {device_id}")
    print(f"Username: {username[:10]}..." if username else "Username: NAO DEFINIDO")
    print(f"Password: {'*' * 10}" if password else "Password: NAO DEFINIDO")
    print("-" * 60)
    
    if not username or not password:
        print("ERRO: Username ou Password nao definidos no .env")
        return False
    
    if username == "seu_token_aqui" or password == "seu_token_aqui":
        print("ERRO: Token nao foi configurado corretamente")
        print("Substitua 'seu_token_aqui' pelo token real do Tago.io")
        return False
    
    # Criar cliente MQTT
    client = mqtt.Client()
    client.username_pw_set(username, password)
    
    # Configurar SSL/TLS
    context = ssl.create_default_context()
    client.tls_set_context(context)
    
    # Callbacks para diagnóstico
    def on_connect(client, userdata, flags, rc):
        print(f"Callback on_connect: Codigo {rc}")
        if rc == 0:
            print("SUCESSO: Conectado ao broker MQTT!")
        else:
            print(f"ERRO: Falha na conexao. Codigo: {rc}")
            print("Codigos de erro MQTT:")
            print("  0: Conexao aceita")
            print("  1: Protocolo incorreto")
            print("  2: Client ID invalido")
            print("  3: Servidor indisponivel")
            print("  4: Username/Password incorretos")
            print("  5: Nao autorizado")
    
    def on_disconnect(client, userdata, rc):
        print(f"Callback on_disconnect: Codigo {rc}")
    
    def on_log(client, userdata, level, buf):
        print(f"Log MQTT: {buf}")
    
    # Configurar callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    
    try:
        print("Tentando conectar...")
        client.connect(host, port, 60)
        client.loop_start()
        
        # Aguardar conexão
        time.sleep(5)
        
        if client.is_connected():
            print("SUCESSO: Conexao estabelecida!")
            
            # Testar envio de dados
            print("Testando envio de dados...")
            topic = f"tago/data/{device_id}"
            test_data = '{"device":"' + device_id + '","data":[{"variable":"test","value":1,"unit":"test"}]}'
            
            result = client.publish(topic, test_data, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("SUCESSO: Dados de teste enviados!")
            else:
                print(f"ERRO: Falha ao enviar dados. Codigo: {result.rc}")
            
            client.disconnect()
            return True
        else:
            print("ERRO: Conexao nao estabelecida")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"ERRO: Excecao durante conexao: {e}")
        return False

if __name__ == "__main__":
    test_connection()
