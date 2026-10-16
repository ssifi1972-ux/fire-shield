import math
import random
import logging
from typing import List, Dict, Tuple, Any

logger = logging.getLogger(__name__)


EXTINGUISHER_COLORS = {
    "red":     "water",
    "yellow":  "wet_chemical",
    "white":   "foam",
    "black":   "co2",
    "blue":    "dry_powder",
}


class Drone:
    """Un drone du swarm avec sa cargaison et son etat"""

    def __init__(self, drone_id: str, color: str, position: Tuple[float, float, float]):
        self.id = drone_id
        self.color = color
        self.extinguisher = EXTINGUISHER_COLORS.get(color, "water")
        self.position = position
        self.velocity = (0.0, 0.0, 0.0)
        self.battery = 100.0
        self.payload = 4
        self.status = "idle"
        self.gyro = (0.0, 0.0, 0.0)
        self.balls_dropped = 0

    def distance_to(self, target: Tuple[float, float, float]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, target)))

    def __repr__(self):
        return f"Drone({self.id}, {self.color}, payload={self.payload}, battery={self.battery:.0f}%)"


class Fleet:
    """Swarm de 10 drones qui suivent les regles de Boids"""

    FORMATION_OFFSETS = [
        (0, 0, 0),
        (-20, -15, 0),
        (20, -15, 0),
        (-30, -35, 0),
        (0, -35, 0),
        (30, -35, 0),
        (-40, -55, 0),
        (-10, -55, 0),
        (10, -55, 0),
        (40, -55, 0),
    ]

    COLORS = ["red", "yellow", "white", "black", "blue",
              "red", "yellow", "white", "black", "blue"]

    def __init__(self, base_gps: Tuple[float, float], department_code: str = "16"):
        self.base_gps = base_gps
        self.department_code = department_code
        self.drones: List[Drone] = []
        self.formation = "triangle"
        self.center = (base_gps[0], base_gps[1], 0.0)
        self._build_swarm()

    def _build_swarm(self):
        """Cree les 10 drones avec numerotation nationale DZ-WW-CC-PP-NN"""
        for i, (dx, dy, dz) in enumerate(self.FORMATION_OFFSETS):
            drone_id = f"DZ-{self.department_code}-01-01-{i+1:02d}"
            pos = (self.base_gps[0] + dx, self.base_gps[1] + dy, 50.0 + dz)
            self.drones.append(Drone(drone_id, self.COLORS[i], pos))

    def select_drones_for_fire(self, fire_type: str) -> List[Drone]:
        """Selectionne les drones appropries selon le type de feu"""
        mapping = {
            "forest":     ["red", "yellow", "red"],
            "building":   ["black", "white", "blue"],
            "industrial": ["black", "blue", "black"],
            "oil":        ["white", "blue", "white"],
            "electrical": ["black"],
        }
        wanted_colors = list(mapping.get(fire_type, ["red"]))
        selected = []
        for drone in self.drones:
            if drone.color in wanted_colors and drone.status == "idle":
                selected.append(drone)
                wanted_colors.remove(drone.color)
                if not wanted_colors:
                    break
        return selected

    def deploy(self, target: Tuple[float, float, float], fire_type: str) -> List[str]:
        """Deploie les drones vers la cible"""
        selected = self.select_drones_for_fire(fire_type)
        for drone in selected:
            drone.status = "flying"
            drone.position = (
                target[0] + random.uniform(-10, 10),
                target[1] + random.uniform(-10, 10),
                target[2] + 30,
            )
            drone.battery -= 5

        logger.info(f"Deploiement : {len(selected)} drones vers {target}")
        return [d.id for d in selected]

    def drop_balls(self, drone_ids: List[str]) -> Dict[str, int]:
        """Chaque drone largue ses 4 balles a 90 degres d'ecart"""
        results = {}
        for drone in self.drones:
            if drone.id in drone_ids and drone.status == "flying":
                dropped = drone.payload
                drone.payload = 0
                drone.balls_dropped = dropped
                drone.status = "returning"
                results[drone.id] = dropped
                logger.info(f"{drone.id} largue {dropped} balles (radial 0/90/180/270)")
        return results

    def return_to_base(self) -> int:
        """Retour au bercail en formation spirale"""
        count = 0
        for drone in self.drones:
            if drone.status == "returning":
                drone.position = (
                    self.base_gps[0] + random.uniform(-5, 5),
                    self.base_gps[1] + random.uniform(-5, 5),
                    5.0,
                )
                drone.status = "idle"
                drone.battery -= 3
                count += 1
        logger.info(f"{count} drones rentres a la base")
        return count

    def boids_update(self):
        """Mise a jour selon les 3 regles de Boids"""
        for drone in self.drones:
            if drone.status != "flying":
                continue
            drone.velocity = tuple(v + random.uniform(-0.5, 0.5) for v in drone.velocity)

    def status_report(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": d.id,
                "color": d.color,
                "extinguisher": d.extinguisher,
                "status": d.status,
                "payload": d.payload,
                "battery": round(d.battery, 1),
            }
            for d in self.drones
        ]