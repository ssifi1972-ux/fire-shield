import httpx
import logging
from typing import List
from state import PublishPackage

logger = logging.getLogger(__name__)

N8N_WEBHOOK_URL = "https://safisafi.app.n8n.cloud/webhook/fire-shield-publish"

async def send_to_n8n(packages: List[PublishPackage]) -> dict:
    """Envoie les packages a n8n via Webhook"""

    if not N8N_WEBHOOK_URL or "your-n8n" in N8N_WEBHOOK_URL:
        logger.warning("N8N non configure - mode simulation")
        for pkg in packages:
            logger.info(f"  Simulation [{pkg['platform']}] : {pkg['content'][:60]}...")
        return {"success": True, "mode": "simulation", "count": len(packages)}

    payload = {
        "packages": packages,
        "source": "fire-shield-langgraph",
    }

    headers = {
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Envoi de {len(packages)} package(s) a n8n...")
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"Publication reussie : status={response.status_code}")
            return {"success": True, "status": response.status_code}
        except httpx.HTTPStatusError as e:
            logger.error(f"Echec HTTP : {e.response.status_code}")
            return {"success": False, "error": str(e)}
        except httpx.RequestError as e:
            logger.error(f"Echec de connexion : {e}")
            return {"success": False, "error": str(e)}