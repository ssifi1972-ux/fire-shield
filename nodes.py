import logging
import random
import time
from state import AgentState, FireAlert, FireAnalysis, PublishPackage
from sensors import SensorSuite, TowerCamera
from drone_fleet import Fleet
from black_box import get_registry
from webhook_client import send_to_n8n

logger = logging.getLogger(__name__)


async def detection_node(state: AgentState) -> AgentState:
    """Detecte un feu via les cameras thermiques sur pylones GSM"""
    logger.info("[detection] Scan des pylones GSM...")

    if state.get("error"):
        return {}

    try:
        tower_id = f"DZ-{random.randint(1, 58):02d}-01-01"
        gps = (round(random.uniform(30, 37), 4), round(random.uniform(-2, 9), 4))
        camera = TowerCamera(tower_id, gps)
        scan = camera.scan()

        if not scan["anomaly_detected"]:
            logger.info("[detection] Aucune anomalie detectee")
            return {"error": "Aucun feu detecte"}

        alert = FireAlert(
            alert_id=f"ALERT-{int(time.time())}",
            tower_id=tower_id,
            gps=gps,
            temperature=scan["temperature"],
            smoke_density=scan["smoke_density"],
            detected_at=time.time(),
            severity="high" if scan["temperature"] > 200 else "medium",
        )

        logger.info(f"[detection] ALERTE - Tour {tower_id} - Temp {scan['temperature']}C")
        return {"fire_alert": alert}

    except Exception as e:
        logger.exception("[detection] Echec")
        return {"error": f"Echec de detection : {e}"}


async def analysis_node(state: AgentState) -> AgentState:
    """Analyse le feu - type, surface, hauteur, vent"""
    logger.info("[analysis] Analyse du feu en cours...")

    if state.get("error"):
        return {}

    try:
        alert = state.get("fire_alert", {})
        temp = alert.get("temperature", 100)

        if temp > 400:
            fire_type = "industrial"
        elif temp > 250:
            fire_type = "forest"
        elif temp > 150:
            fire_type = "building"
        else:
            fire_type = "electrical"

        intensity = min(1.0, temp / 400)

        analysis = FireAnalysis(
            fire_type=fire_type,
            area_m2=round(random.uniform(50, 800) * intensity, 1),
            height_m=round(random.uniform(3, 25) * intensity, 1),
            wind_speed=round(random.uniform(5, 35), 1),
            wind_direction=round(random.uniform(0, 360), 1),
            humidity=round(random.uniform(10, 40), 1),
            spread_speed=round(random.uniform(2, 15) * intensity, 1),
            risk_level="critical" if intensity > 0.7 else "high",
        )

        logger.info(f"[analysis] Type: {fire_type}, Surface: {analysis['area_m2']} m2")
        return {"fire_analysis": analysis}

    except Exception as e:
        logger.exception("[analysis] Echec")
        return {"error": f"Echec d'analyse : {e}"}


async def dispatch_node(state: AgentState) -> AgentState:
    """Deploie le swarm de 10 drones en formation triangulaire"""
    logger.info("[dispatch] Deploiement du swarm...")

    if state.get("error"):
        return {}

    try:
        alert = state.get("fire_alert", {})
        analysis = state.get("fire_analysis", {})
        gps = alert.get("gps", (36.75, 3.05))

        fleet = Fleet(base_gps=gps, department_code="16")

        registry = get_registry()
        for drone in fleet.drones:
            registry.get_or_create(drone.id)
            registry.boxes[drone.id].record("drone_initialized", {
                "color": drone.color,
                "extinguisher": drone.extinguisher,
                "payload_kg": 20,
            })

        target = (gps[0] + random.uniform(-0.01, 0.01),
                  gps[1] + random.uniform(-0.01, 0.01),
                  30.0)

        deployed = fleet.deploy(target, analysis.get("fire_type", "forest"))

        registry.record_all("fleet_deployed", {
            "target": target,
            "drones": deployed,
            "fire_type": analysis.get("fire_type"),
        })

        logger.info(f"[dispatch] {len(deployed)} drones deployes")
        return {"deployed_drones": deployed}

    except Exception as e:
        logger.exception("[dispatch] Echec")
        return {"error": f"Echec de deploiement : {e}"}


async def intervention_node(state: AgentState) -> AgentState:
    """Les drones larguent leurs balles (largage radial)"""
    logger.info("[intervention] Largage des balles...")

    if state.get("error"):
        return {}

    try:
        alert = state.get("fire_alert", {})
        analysis = state.get("fire_analysis", {})
        deployed = state.get("deployed_drones", [])

        if not deployed:
            return {"error": "Aucun drone deploye"}

        gps = alert.get("gps", (36.75, 3.05))
        fleet = Fleet(base_gps=gps, department_code="16")

        for drone in fleet.drones:
            if drone.id in deployed:
                drone.status = "flying"

        sensor = SensorSuite(deployed[0])
        readings = sensor.read_all(fire_intensity=0.8)
        signature = sensor.detect_fire_signature()

        drops = fleet.drop_balls(deployed)

        registry = get_registry()
        for drone_id, balls in drops.items():
            registry.boxes[drone_id].record("balls_dropped", {
                "balls_count": balls,
                "angle_pattern": [0, 90, 180, 270],
                "sensor_readings": readings,
                "fire_signature": signature,
            })

        returned = fleet.return_to_base()

        result = {
            "drops": drops,
            "total_balls": sum(drops.values()),
            "total_mass_kg": sum(drops.values()) * 5,
            "returned_drones": returned,
            "sensor_readings": readings,
            "fire_signature": signature,
        }

        logger.info(f"[intervention] {result['total_balls']} balles larguees ({result['total_mass_kg']} kg)")
        return {"intervention_result": result}

    except Exception as e:
        logger.exception("[intervention] Echec")
        return {"error": f"Echec d'intervention : {e}"}


async def coordination_node(state: AgentState) -> AgentState:
    """Envoie des signaux UHF/VHF"""
    logger.info("[coordination] Emission des signaux UHF/VHF...")

    if state.get("error"):
        return {}

    try:
        alert = state.get("fire_alert", {})
        analysis = state.get("fire_analysis", {})
        intervention = state.get("intervention_result", {})

        signals = [
            {
                "agency": "Protection Civile",
                "frequency": "UHF 433.500 MHz",
                "message": f"Feu {analysis.get('fire_type')} a {alert.get('gps')} - "
                           f"Surface {analysis.get('area_m2')} m2 - "
                           f"Intervention terminee : {intervention.get('total_balls')} balles",
                "priority": "critical",
            },
            {
                "agency": "Direction des Forets",
                "frequency": "VHF 155.725 MHz",
                "message": f"Feu de foret - Zone {alert.get('tower_id')} - "
                           f"Humidite {analysis.get('humidity')}% - "
                           f"Vent {analysis.get('wind_speed')} km/h",
                "priority": "high",
            },
            {
                "agency": "Gendarmerie Nationale",
                "frequency": "UHF 410.200 MHz",
                "message": f"Incident {alert.get('alert_id')} - Rapport black box en preparation",
                "priority": "medium",
            },
        ]

        logger.info(f"[coordination] {len(signals)} signaux envoyes")
        return {"coordination_signals": signals}

    except Exception as e:
        logger.exception("[coordination] Echec")
        return {"error": f"Echec de coordination : {e}"}


async def publish_node(state: AgentState) -> AgentState:
    """Prepare et publie le rapport final"""
    logger.info("[publish] Preparation du rapport final...")

    if state.get("error"):
        return {}

    try:
        alert = state.get("fire_alert", {})
        analysis = state.get("fire_analysis", {})
        intervention = state.get("intervention_result", {})

        registry = get_registry()
        bb_report = registry.global_report()

        content_fr = (
            f"Feu {analysis.get('fire_type')} maitrise\n"
            f"Position {alert.get('tower_id')} - {alert.get('gps')}\n"
            f"Temperature {alert.get('temperature')}C\n"
            f"{intervention.get('total_balls')} balles larguees "
            f"({intervention.get('total_mass_kg')} kg)\n"
            f"{len(state.get('deployed_drones', []))} drones deployes\n"
            f"Black Box : {bb_report['total_boxes']} boites verifiees\n"
            f"Integrite : {bb_report['all_verified']}\n"
            f"#FireShield #Algeria #Souverainete"
        )

        drafts = [
            PublishPackage(
                platform="x",
                content=content_fr,
                image_url=None,
                language="fr",
            ),
            PublishPackage(
                platform="linkedin",
                content=content_fr + "\n\n#FireSafety #AI #Drones",
                image_url=None,
                language="fr",
            ),
        ]

        logger.info(f"[publish] {len(drafts)} drafts prepares")

        publish_result = await send_to_n8n(drafts)
        logger.info(f"[publish] Resultat n8n : {publish_result}")

        return {
            "drafts": drafts,
            "translated_drafts": drafts,
            "black_box_report": bb_report,
            "publish_result": publish_result,
        }

    except Exception as e:
        logger.exception("[publish] Echec")
        return {"error": f"Echec de publication : {e}"}