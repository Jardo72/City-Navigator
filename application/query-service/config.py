from os import environ


class Config:

    @staticmethod
    def get_master_data_service_base_url() -> str:
        return Config._get_environment_variable("MASTER_DATA_SERVICE_BASE_URL", "http://localhost:90")

    @staticmethod
    def get_database_url() -> str:
        return Config._get_environment_variable("DATABASE_URL", "sqlite://")

    @staticmethod
    def _get_environment_variable(name: str, default_value: str) -> str:
        result = environ[name]
        if result is None:
            result = default_value
        return result
