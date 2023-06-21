from abc import ABC, abstractmethod

from pydantic import BaseModel


class AbstractModule(ABC, BaseModel):
    @abstractmethod
    def run(self):
        pass


class AbstractContextManager(ABC, BaseModel):
    @abstractmethod
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass
