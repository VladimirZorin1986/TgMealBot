from dataclasses import dataclass
from environs import Env
from aiogram.fsm.storage.memory import MemoryStorage, BaseStorage


@dataclass
class DatabaseConfig:
    db_name: str
    user: str
    password: str
    host: str
    port: str
    driver: str

    def __post_init__(self):
        self.dsn = f'postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'
        self.url = f'postgresql+{self.driver}://{self.user}:{self.password}@{self.host}/{self.db_name}'


@dataclass
class BotConfig:
    token: str
    storage: BaseStorage
    admin_ids: list[int]


@dataclass
class Config:
    bot: BotConfig
    db: DatabaseConfig


def load_config() -> Config:
    env: Env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            token=env('BOT_TOKEN'),
            storage=MemoryStorage(),
            admin_ids=[int(admin_id) for admin_id in env.list('ADMIN_IDS')]
        ),
        db=DatabaseConfig(
            db_name=env('DB_NAME'),
            user=env('DB_USER'),
            password=env('DB_PASSWORD'),
            host=env('DB_HOST'),
            port=env('DB_PORT'),
            driver=env('DB_DRIVER')
        )
    )
