# datasource.py
from abc import ABC, abstractmethod

class DataSource(ABC):
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def stop(self): ...