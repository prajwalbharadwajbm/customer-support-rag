from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger(__name__)

class PromptAnalysis(BaseModel):
    attackDetected: bool
    def __init__(self, **data):
        super().__init__(**data)       
        logger.debug(f"PromptAnalysis done with attack_detected: %s",self.attackDetected)


class ContentSafetyRequest(BaseModel):
    userPrompt: str
    def __init__(self, **data):
        super().__init__(**data)       
        logger.debug(f"ContentSafetyRequest done with userPrompt: %s",self.userPrompt)

class ContentSafetyResponse(BaseModel):
    userPromptAnalysis: PromptAnalysis
    def __init__(self, **data):
        super().__init__(**data)       
        logger.debug(f"ContentSafetyResponse generated with userPromptAnalysis: %s",self.userPromptAnalysis)

