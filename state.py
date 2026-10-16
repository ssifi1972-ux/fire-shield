from typing import TypedDict, List, Optional, Dict, Any


class FireAlert(TypedDict):
    """Alerte de feu detectee par une camera thermique"""
    alert_id: str
    tower_id: str
    gps: tuple
    temperature: float
    smoke_density: float
    detected_at: float
    severity: str


class FireAnalysis(TypedDict):
    """Analyse du feu par l'agent AI"""
    fire_type: str
    area_m2: float
    height_m: float
    wind_speed: float
    wind_direction: float
    humidity: float
    spread_speed: float
    risk_level: str


class PublishPackage(TypedDict):
    """Package de publication"""
    platform: str
    content: str
    image_url: Optional[str]
    language: str


class AgentState(TypedDict, total=False):
    """Etat partage entre les noeuds LangGraph"""
    user_command: str
    fire_alert: FireAlert
    fire_analysis: FireAnalysis
    deployed_drones: List[str]
    fleet_instance: Any
    intervention_result: Dict[str, Any]
    coordination_signals: List[Dict[str, Any]]
    drafts: List[PublishPackage]
    translated_drafts: List[PublishPackage]
    publish_result: dict
    black_box_report: dict
    error: Optional[str]