from abc import ABC, abstractmethod

from pydantic import BaseModel


class AbstractModule(ABC, BaseModel):
    @abstractmethod
    def run(self, **kwargs):
        pass


class AbstractContextManager(ABC, BaseModel):
    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass
