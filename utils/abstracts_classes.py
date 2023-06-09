from abc import ABC, abstractmethod


class AbstractModule(ABC):
    @abstractmethod
    def run(self):
        pass
