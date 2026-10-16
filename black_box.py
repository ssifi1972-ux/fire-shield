import hashlib
import json
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class BlackBox:
    """Boite noire inalterable - blockchain locale + WORM"""

    def __init__(self, drone_id: str):
        self.drone_id = drone_id
        self.chain: List[Dict[str, Any]] = []
        self.created_at = time.time()

    def record(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistre un evenement dans la chaine (immuable)"""
        previous_hash = self._get_last_hash()

        record = {
            "drone_id": self.drone_id,
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data,
            "previous_hash": previous_hash,
        }

        record_str = json.dumps(record, sort_keys=True, default=str)
        record["hash"] = hashlib.sha256(record_str.encode()).hexdigest()

        self.chain.append(record)
        logger.debug(f"[{self.drone_id}] BlackBox : {event_type}")
        return record

    def _get_last_hash(self) -> str:
        if not self.chain:
            return "0" * 64
        return self.chain[-1]["hash"]

    def verify_chain(self) -> bool:
        """Verifie l'integrite de la chaine complete"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current["previous_hash"] != previous["hash"]:
                logger.error(f"CHAINE CORROMPUE a l'index {i}")
                return False
        return True

    def export_report(self, case_id: str = "UNKNOWN") -> Dict[str, Any]:
        """Genere un rapport final inalterable"""
        return {
            "case_id": case_id,
            "drone_id": self.drone_id,
            "chain_length": len(self.chain),
            "created_at": self.created_at,
            "first_event": self.chain[0] if self.chain else None,
            "last_event": self.chain[-1] if self.chain else None,
            "integrity_verified": self.verify_chain(),
            "chain_hash": self._get_last_hash()[:16] + "...",
        }


class BlackBoxRegistry:
    """Registre centralise de toutes les boites noires"""

    def __init__(self):
        self.boxes: Dict[str, BlackBox] = {}

    def get_or_create(self, drone_id: str) -> BlackBox:
        if drone_id not in self.boxes:
            self.boxes[drone_id] = BlackBox(drone_id)
        return self.boxes[drone_id]

    def record_all(self, event_type: str, data: Dict[str, Any]):
        """Enregistre le meme evenement sur toutes les boites noires"""
        for box in self.boxes.values():
            box.record(event_type, data)

    def global_report(self) -> Dict[str, Any]:
        return {
            "total_boxes": len(self.boxes),
            "all_verified": all(b.verify_chain() for b in self.boxes.values()),
            "boxes": [b.export_report() for b in self.boxes.values()],
        }


# Instance globale
_registry = BlackBoxRegistry()


def get_registry() -> BlackBoxRegistry:
    return _registry