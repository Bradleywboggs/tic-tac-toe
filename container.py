import dataclasses
import os
from enum import Enum
from typing import Callable

from redis.client import Redis

from data_source.data_source import DataSource
from data_source.in_memory_data_source import (
    InMemoryDataSource,
    in_memory_data_source,
)
from data_source.redis_data_source import RedisDataSource


class Env(Enum):
    Test = "test"
    Prod = "prod"


class BaseUrl(Enum):
    Local = "http://localhost:8000"
    Prod = "http://localhost:8000"


@dataclasses.dataclass
class Container:
    data_sources: dict[Env, Callable[[], DataSource]]
    base_urls: dict[Env, BaseUrl]


container = Container(
    data_sources={
        Env.Test: lambda: in_memory_data_source,
        Env.Prod: lambda: RedisDataSource(
            Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", 6379)),
            )
        ),
    },
    base_urls={Env.Test: BaseUrl.Local, Env.Prod: BaseUrl.Prod},
)
