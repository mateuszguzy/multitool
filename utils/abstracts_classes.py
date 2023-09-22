from abc import ABC, abstractmethod
from typing import Any


class AbstractModule(ABC):
    """
    AbstractModule is a base class for implementing modules.
    It provides an interface for running the module.
    """
    @abstractmethod
    def run(self) -> Any:
        """
        Run the module with the given arguments.

        Returns:
            The result of running the module.
        """
        pass


class AbstractContextManager(ABC):
    """
    Abstract class for all context managers.
    """

    @abstractmethod
    def __enter__(self) -> Any:
        """
        Enter the context and return the context manager object.
        """
        raise NotImplementedError("Subclasses must implement the __enter__ method.")

    @abstractmethod
    def __exit__(self, exc_type: type, exc_value: BaseException, exc_traceback: BaseException) -> Any:
        """
        Exit the context and handle any exceptions raised within the context.
        """
        raise NotImplementedError("Subclasses must implement the __exit__ method.")
