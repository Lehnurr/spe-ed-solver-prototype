from abc import abstractmethod
from abc import ABC


class BaseConnector(ABC):

    @abstractmethod
    def start(self):
        raise NotImplementedError
