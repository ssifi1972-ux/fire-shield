import logging
import urllib.parse

logger = logging.getLogger(__name__)


def generate_image_url(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """
    Genere une URL d'image via Pollinations AI (gratuit, sans cle API).
    Retourne l'URL de l'image generee.
    """
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
        logger.info(f"Image generee : {url[:60]}...")
        return url
    except Exception as e:
        logger.error(f"Erreur de generation d'image : {e}")
        return ""


def generate_image_for_package(package: dict) -> dict:
    """
    Genere une image pour un package de publication base sur son contenu.
    """
    content = package.get("content", "")
    platform = package.get("platform", "")

    # Adapter le prompt selon la plateforme
    if platform == "tiktok" or platform == "instagram":
        prompt = f"Modern social media visual, {content[:100]}, vibrant colors, eye-catching"
        width, height = 1080, 1920  # Format vertical
    else:
        prompt = f"Professional social media image, {content[:100]}, clean design, modern"
        width, height = 1200, 630  # Format horizontal

    url = generate_image_url(prompt, width, height)
    package["image_url"] = url
    return package