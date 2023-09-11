from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    env_file: str = '.env'
    env = SettingsConfigDict(env_file=env_file, env_file_encoding='utf-8')