from motor.motor import Motor


class DummyMotor(Motor):
    def __init__(self):
        self.speed = 0

    def set_speed(self, speed: float) -> None:
        print(f'[DUMMY MOTOR] {speed=}')
        self.speed = speed

    def get_speed(self) -> float:
        return self.speed
