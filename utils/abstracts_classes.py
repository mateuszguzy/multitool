from abc import ABC, abstractmethod

from pydantic import BaseModel


class AbstractModule(ABC, BaseModel):
    @abstractmethod
    def run(self, **kwargs):
        pass


class AbstractBaseContextManager(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class AbstractContextManager(AbstractBaseContextManager, BaseModel):
    @abstractmethod
    def __init__(self):
        super().__init__()


class AbstractRedisContextManager(AbstractBaseContextManager):
    @abstractmethod
    def __init__(self):
        super().__init__()
