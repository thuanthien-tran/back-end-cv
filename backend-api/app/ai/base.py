from abc import ABC, abstractmethod


class AIService(ABC):
    @abstractmethod
    def generate_feedback(self, matching_result: dict) -> dict:
        pass
