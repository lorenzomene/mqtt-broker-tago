import json
import ssl
import time
from typing import Dict, List, Any
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os


class TagoMQTTClient:
    """Cliente MQTT para comunicação com Tago.io"""
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback chamado quando conecta ao broker"""
        if rc == 0:
            print(f" Conectado ao broker MQTT: {self.host}:{self.port}")
            self.connected = True
        else:
            print(f" Falha na conexão MQTT. Código: {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback chamado quando desconecta do broker"""
        print(f" Desconectado do broker MQTT. Código: {rc}")
        self.connected = False
    
    def on_publish(self, client, userdata, mid):
        """Callback chamado quando publica uma mensagem"""
        print(f" Mensagem publicada com sucesso (ID: {mid})")
    
    def connect(self):
        """Conecta ao broker MQTT"""
        try:
            self.client = mqtt.Client()
            self.client.username_pw_set(self.username, self.password)
            
            # Configurar callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            # Configurar SSL/TLS para conexão segura
            context = ssl.create_default_context()
            self.client.tls_set_context(context)
            
            # Conectar ao broker
            print(f" Conectando ao broker MQTT: {self.host}:{self.port}")
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            
            # Aguardar conexão
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
            
        except Exception as e:
            print(f" Erro ao conectar ao broker MQTT: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do broker MQTT"""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            print(" Desconectado do broker MQTT")
    
    def publish_sensor_data(self, device_id: str, sensor_data: List[Dict[str, Any]]) -> bool:
        """Publica dados de sensores no Tago.io"""
        if not self.connected:
            print(" Cliente MQTT não está conectado")
            return False
        
        try:
            # Tópico para envio de dados ao Tago.io
            topic = f"tago/data/{device_id}"
            
            # Preparar dados para envio
            payload = {
                "device": device_id,
                "data": sensor_data
            }
            
            # Converter para JSON
            message = json.dumps(payload, ensure_ascii=False)
            
            # Publicar mensagem
            result = self.client.publish(topic, message, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f" Dados enviados para {topic}")
                print(f"   {len(sensor_data)} sensores processados")
                return True
            else:
                print(f" Falha ao publicar dados. Código: {result.rc}")
                return False
                
        except Exception as e:
            print(f" Erro ao publicar dados: {e}")
            return False
    
    def publish_single_sensor(self, device_id: str, sensor_data: Dict[str, Any]) -> bool:
        """Publica dados de um único sensor"""
        return self.publish_sensor_data(device_id, [sensor_data])


def create_mqtt_client_from_env() -> TagoMQTTClient:
    """Cria cliente MQTT a partir das variáveis de ambiente"""
    load_dotenv()
    
    host = os.getenv('TAGO_MQTT_HOST', 'mqtt.tago.io')
    port = int(os.getenv('TAGO_MQTT_PORT', '8883'))
    username = os.getenv('TAGO_MQTT_USERNAME')
    password = os.getenv('TAGO_MQTT_PASSWORD')
    
    if not username or not password:
        raise ValueError("TAGO_MQTT_USERNAME e TAGO_MQTT_PASSWORD devem ser definidos")
    
    return TagoMQTTClient(host, port, username, password)
