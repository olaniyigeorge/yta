from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from logger import logger

class GlobalConfig(BaseSettings):
    ENV: str = "development"
    PORT: int = 8000
    PROJECT_NAME: str = "YTA"
    CLIENT_DOMAIN: str = "http://localhost:8000"
    GEMINI_API_KEY: str = "test"



    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class DevConfig(GlobalConfig):
    pass

class TestConfig(GlobalConfig):
    pass

class ProdConfig(GlobalConfig):
    pass


def get_config():
    env_state = GlobalConfig().ENV.lower()  # Load from `.env` automatically
    configs = {"development": DevConfig, "production": ProdConfig, "test": TestConfig}
    if env_state not in configs:
        raise ValueError(f"Invalid ENVT_STATE: {env_state}")
    logger.info(f"\nUsing {env_state.capitalize()} config...\n")
    return configs[env_state]()

# Lazy config loading to avoid import-time errors
def get_lazy_config():
    try:
        return get_config()
    except Exception:
        # Return a default config for testing
        class DefaultConfig:
            ENV = "test"
            PORT = 8000
            PROJECT_NAME = "YTA"
            CLIENT_DOMAIN = "http://localhost:8000"
            GEMINI_API_KEY = "test"
        return DefaultConfig()


AppConfig: GlobalConfig = get_lazy_config()