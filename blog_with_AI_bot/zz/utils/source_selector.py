#zz/utils/source_selector.py
from zz.models import GenerationSettings
#from django.core.exceptions import ObjectDoesNotExist

import logging

logger = logging.getLogger(__name__)


def get_active_source() -> str:
    """ Returns currently choiced source LLM from DB"""

    try:
        setting = GenerationSettings.objects.first()
        if setting:
            return setting.current_source
        logger.warning("[GENERATION] !!! Not found GenerationSettings, fallback='ollama'")
        return "ollama"
        
    except Exception as e:
    #except (ObjectDoesNotExist, AttributeError):
        logger.error(f"[GENERATION] ERROR getting source: {e}")
        return "ollama"  # fallback