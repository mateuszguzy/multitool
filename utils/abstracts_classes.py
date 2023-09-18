from abc import ABC, abstractmethod

from pydantic import BaseModel


class AbstractModule(ABC, BaseModel):
    @abstractmethod
    def run(self, **kwargs):
        pass


# TODO: add Pydantic 'BaseModel' as parent
#  current tries give validation errors for Redis and Socket manager
class AbstractContextManager(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
