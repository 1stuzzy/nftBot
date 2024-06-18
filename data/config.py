from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    postgres_uri: str


@dataclass
class TgBot:
    token: str
    control_token: str
    admin_ids: list[int]
    use_redis: bool
    tech_work: int


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Links:
    rules: str
    support: str

@dataclass
class Ids:
    top_up: int

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    links: Links
    ids: Ids


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            control_token=env.str("CONTROL_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            tech_work=env.int("TECH_WORK")
        ),
        db=DbConfig(
            postgres_uri=env.str("POSTGRES_URI")
        ),
        misc=Miscellaneous(),
        links=Links(rules=env.str("LINK_RULES"),
                    support=env.str("SUPPORT_LINK")),
        ids=Ids(top_up=env.int("TOP_UP_ID"))
    )
