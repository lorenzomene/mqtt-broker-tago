import time
import signal
import sys
from datetime import datetime
from sensor_simulator import SensorSimulator
from mqtt_client import create_mqtt_client_from_env
import os
from dotenv import load_dotenv


class IoTDataSimulator:
    """Aplicação principal do simulador IoT"""
    
    def __init__(self):
        load_dotenv()
        
        # Configurações do dispositivo
        self.device_id = os.getenv('DEVICE_ID', 'device_001')
        self.device_name = os.getenv('DEVICE_NAME', 'Sensor_Temperature_001')
        
        # Inicializar componentes
        self.sensor_simulator = SensorSimulator(self.device_id, self.device_name)
        self.mqtt_client = None
        self.running = False
        
        # Configurar handler para interrupção
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        print(f"\n Recebido sinal {signum}. Parando simulador...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Inicia o simulador IoT"""
        print(" Iniciando Simulador IoT para Tago.io")
        print(f" Dispositivo: {self.device_name} (ID: {self.device_id})")
        print("-" * 50)
        
        try:
            # Conectar ao broker MQTT
            print(" Conectando ao broker MQTT...")
            self.mqtt_client = create_mqtt_client_from_env()
            
            if not self.mqtt_client.connect():
                print(" Falha ao conectar ao broker MQTT")
                return False
            
            # Iniciar loop principal
            self.running = True
            self.run_simulation_loop()
            
        except Exception as e:
            print(f" Erro no simulador: {e}")
            return False
        finally:
            self.stop()
    
    def run_simulation_loop(self):
        """Loop principal de simulação"""
        print(" Iniciando loop de simulação...")
        print(" Pressione Ctrl+C para parar")
        print("-" * 50)
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                print(f"\n Iteração {iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Gerar dados dos sensores
                sensor_data = self.sensor_simulator.generate_all_sensor_data()
                
                # Exibir dados gerados
                for data in sensor_data:
                    print(f"   {data['variable']}: {data['value']} {data['unit']}")
                
                # Enviar dados via MQTT
                if self.mqtt_client and self.mqtt_client.connected:
                    success = self.mqtt_client.publish_sensor_data(self.device_id, sensor_data)
                    if success:
                        print("   Dados enviados com sucesso")
                    else:
                        print("   Falha ao enviar dados")
                else:
                    print("   Cliente MQTT não conectado")
                
                # Aguardar próxima iteração (10 segundos)
                print("   Aguardando 10 segundos...")
                time.sleep(10)
                
            except KeyboardInterrupt:
                print("\n Interrupção detectada")
                break
            except Exception as e:
                print(f" Erro no loop de simulação: {e}")
                time.sleep(5)  # Aguardar antes de tentar novamente
    
    def stop(self):
        """Para o simulador"""
        print("\n Parando simulador...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        print(" Simulador parado")


def main():
    """Função principal"""
    print("=" * 60)
    print(" SIMULADOR IoT PARA TAGO.IO")
    print("=" * 60)
    
    # Verificar variáveis de ambiente
    load_dotenv()
    required_vars = ['TAGO_MQTT_USERNAME', 'TAGO_MQTT_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(" Variáveis de ambiente obrigatórias não encontradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n Copie o arquivo 'config.env.example' para '.env' e configure as variáveis")
        return
    
    # Iniciar simulador
    simulator = IoTDataSimulator()
    simulator.start()


if __name__ == "__main__":
    main()
