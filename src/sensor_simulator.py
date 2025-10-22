"""
Simulador de sensores IoT com processamento básico de dados
"""
import random
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Any


class SensorSimulator:
    """Simulador de sensores IoT com processamento de dados"""
    
    def __init__(self, device_id: str, device_name: str):
        self.device_id = device_id
        self.device_name = device_name
        self.data_history = []
        self.max_history = 100  # Manter histórico para processamento
        
    def generate_temperature_data(self) -> Dict[str, Any]:
        """Gera dados simulados de temperatura com variação realística"""
        # Temperatura base com variação sazonal e diária
        base_temp = 25.0
        daily_variation = 5 * np.sin(2 * np.pi * datetime.now().hour / 24)
        seasonal_variation = 3 * np.sin(2 * np.pi * datetime.now().timetuple().tm_yday / 365)
        noise = random.gauss(0, 1.5)
        
        temperature = base_temp + daily_variation + seasonal_variation + noise
        
        return {
            "variable": "temperature",
            "value": round(temperature, 2),
            "unit": "°C",
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "device_name": self.device_name
        }
    
    def generate_humidity_data(self) -> Dict[str, Any]:
        """Gera dados simulados de umidade"""
        # Umidade correlacionada com temperatura
        base_humidity = 60.0
        temp_factor = random.uniform(-0.5, 0.5)
        noise = random.gauss(0, 3)
        
        humidity = base_humidity + temp_factor + noise
        humidity = max(0, min(100, humidity))  # Limitar entre 0-100%
        
        return {
            "variable": "humidity",
            "value": round(humidity, 2),
            "unit": "%",
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "device_name": self.device_name
        }
    
    def generate_vibration_data(self) -> Dict[str, Any]:
        """Gera dados simulados de vibração"""
        # Vibração com padrões periódicos e ruído
        base_vibration = 0.5
        periodic = 2 * np.sin(2 * np.pi * time.time() / 10)  # Ciclo de 10 segundos
        noise = random.gauss(0, 0.3)
        
        vibration = base_vibration + periodic + noise
        vibration = max(0, vibration)  # Vibração não pode ser negativa
        
        return {
            "variable": "vibration",
            "value": round(vibration, 3),
            "unit": "g",
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "device_name": self.device_name
        }
    
    def generate_light_data(self) -> Dict[str, Any]:
        """Gera dados simulados de luminosidade"""
        # Luminosidade baseada no horário do dia
        hour = datetime.now().hour
        if 6 <= hour <= 18:  # Dia
            base_light = 500 + 300 * np.sin(np.pi * (hour - 6) / 12)
        else:  # Noite
            base_light = 50
        
        noise = random.gauss(0, 20)
        light = base_light + noise
        light = max(0, light)
        
        return {
            "variable": "light",
            "value": round(light, 2),
            "unit": "lux",
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "device_name": self.device_name
        }
    
    def remove_outliers(self, data: List[float], threshold: float = 2.0) -> List[float]:
        """Remove outliers usando método Z-score"""
        if len(data) < 3:
            return data
            
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return data
            
        filtered_data = []
        for value in data:
            z_score = abs(value - mean) / std
            if z_score <= threshold:
                filtered_data.append(value)
            else:
                # Substituir outlier pela média dos valores válidos
                filtered_data.append(mean)
        
        return filtered_data
    
    def process_sensor_data(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados do sensor aplicando filtros e validações"""
        variable = sensor_data["variable"]
        value = sensor_data["value"]
        
        # Adicionar ao histórico
        self.data_history.append(value)
        if len(self.data_history) > self.max_history:
            self.data_history.pop(0)
        
        # Aplicar filtro de outliers se temos histórico suficiente
        if len(self.data_history) >= 5:
            filtered_values = self.remove_outliers(self.data_history)
            if filtered_values:
                sensor_data["value"] = round(filtered_values[-1], 2)
        
        # Adicionar metadados de processamento
        sensor_data["processed"] = True
        sensor_data["quality"] = "good" if len(self.data_history) >= 3 else "initializing"
        
        return sensor_data
    
    def generate_all_sensor_data(self) -> List[Dict[str, Any]]:
        """Gera dados de todos os sensores simulados"""
        sensors = [
            self.generate_temperature_data(),
            self.generate_humidity_data(),
            self.generate_vibration_data(),
            self.generate_light_data()
        ]
        
        # Processar dados de cada sensor
        processed_sensors = []
        for sensor_data in sensors:
            processed_data = self.process_sensor_data(sensor_data)
            processed_sensors.append(processed_data)
        
        return processed_sensors
