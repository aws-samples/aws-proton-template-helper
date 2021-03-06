from enum import Enum

class TemplateType(Enum):
    ENVIRONMENT = 1
    SERVICE = 2
    SERVICE_WITHOUT_PIPELINE = 3

class ResourceType(Enum):
    ENVIRONMENT = 1
    SERVICE_INSTANCE = 2
    SERVICE_PIPELINE = 3