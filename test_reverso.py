import random
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SensorSuite:
    """Huit capteurs sur chaque drone - pas de camera (vision claire)"""

    def __init__(self, drone_id: str):
        self.drone_id = drone_id
        self.readings: Dict[str, float] = {}

    def read_all(self, fire_intensity: float = 0.5) -> Dict[str, Any]:
        """Lit tous les capteurs en tenant compte de l'intensite du feu"""
        intensity = max(0.0, min(1.0, fire_intensity))

        self.readings = {
            "temperature_ir": round(20 + intensity * 320 + random.uniform(-5, 5), 1),
            "smoke_density": round(intensity * 95 + random.uniform(-5, 5), 1),
            "co_ppm": round(intensity * 800 + random.uniform(-50, 50), 1),
            "so2_ppm": round(intensity * 40 + random.uniform(-5, 5), 1),
            "voc_ppm": round(intensity * 120 + random.uniform(-10, 10), 1),
            "humidity": round(30 - intensity * 25 + random.uniform(-3, 3), 1),
            "wind_speed": round(random.uniform(5, 35), 1),
            "wind_direction": round(random.uniform(0, 360), 1),
        }

        logger.debug(f"[{self.drone_id}] Capteurs : {self.readings}")
        return self.readings

    def detect_fire_signature(self) -> Dict[str, str]:
        """Analyse la signature chimique du feu"""
        profile: Dict[str, str] = {}

        if self.readings.get("co_ppm", 0) > 300:
            profile["combustion"] = "active"
        if self.readings.get("so2_ppm", 0) > 15:
            profile["fuel"] = "vegetation"
        if self.readings.get("voc_ppm", 0) > 60:
            profile["fuel"] = "industrial_chemicals"
        if self.readings.get("temperature_ir", 0) > 200:
            profile["intensity"] = "high"

        return profile


class TowerCamera:
    """Camera thermique sur pylone GSM"""

    def __init__(self, tower_id: str, gps: tuple):
        self.tower_id = tower_id
        self.gps = gps
        self.active = True

    def scan(self) -> Dict[str, Any]:
        """Scan une zone autour du pylone"""
        anomaly = random.random() < 0.15  # 15% de chance de detecter

        return {
            "tower_id": self.tower_id,
            "gps": self.gps,
            "anomaly_detected": anomaly,
            "temperature": round(random.uniform(25, 400) if anomaly else random.uniform(20, 35), 1),
            "smoke_density": round(random.uniform(30, 95) if anomaly else random.uniform(0, 10), 1),
        }