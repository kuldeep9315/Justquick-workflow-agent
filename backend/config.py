import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')
    HUBSPOT_BASE_URL = "https://api.hubapi.com"
    DEBUG = os.getenv('DEBUG', False)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Workflow defaults
    DEFAULT_WORKFLOW_ENABLED = True
    
    # API versions
    AUTOMATION_API_V3 = "/automation/v3"
    AUTOMATION_API_V4 = "/automation/v4"
    CRM_API_V3 = "/crm/v3"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
