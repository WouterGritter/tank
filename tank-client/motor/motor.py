from abc import ABC, abstractmethod


class Motor(ABC):
    @abstractmethod
    def set_speed(self, speed: float) -> None:
        pass

    @abstractmethod
    def get_speed(self) -> float:
        pass

    def change_speed(self, speed_delta: float) -> None:
        self.set_speed(self.get_speed() + speed_delta)
