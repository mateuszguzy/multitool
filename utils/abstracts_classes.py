from abc import ABC, abstractmethod

from pydantic import BaseModel


class AbstractModule(ABC, BaseModel):
    @abstractmethod
    def run(self):
        pass
