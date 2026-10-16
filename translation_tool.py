import logging
from typing import List
from state import PublishPackage
from translatepy import Translator

logger = logging.getLogger(__name__)

_translator = Translator()


def translate_text(text: str, source_lang: str = "en", target_lang: str = "fr") -> str:
    try:
        result = _translator.translate(text, source_language=source_lang, destination_language=target_lang)
        translated = str(result)
        if translated and translated != text:
            logger.info(f"Traduction reussie : {text[:30]}... -> {translated[:30]}...")
            return translated
        logger.warning("Traduction vide, retour du texte original")
        return text
    except Exception as e:
        logger.error(f"Erreur de traduction : {e}")
        return text


def translate_packages(packages: List[PublishPackage], target_lang: str = "fr") -> List[PublishPackage]:
    translated = []
    for pkg in packages:
        translated_content = translate_text(
            pkg["content"],
            source_lang=pkg.get("language", "en"),
            target_lang=target_lang
        )
        new_pkg = PublishPackage(
            platform=pkg["platform"],
            content=translated_content,
            image_url=pkg.get("image_url"),
            language=target_lang
        )
        translated.append(new_pkg)
    logger.info(f"{len(translated)} packages traduits vers {target_lang}")
    return translated