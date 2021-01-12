from abc import ABC, abstractmethod
import logging


class ILoggerFactory(ABC):
    @abstractmethod
    def getLogger(self, name: str) -> logging.Logger:
        pass


class LoggerFactory(ILoggerFactory):
    def __init__(self) -> None:
        super().__init__()

    def getLogger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)