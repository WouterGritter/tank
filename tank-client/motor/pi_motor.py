import time
from threading import Thread

import RPi.GPIO as GPIO

from motor.motor import Motor


class PiMotor(Motor):
    def __init__(self, pin_a, pin_b, update_delay=0.002):
        self.update_delay = update_delay

        GPIO.setup(pin_a, GPIO.OUT)
        GPIO.setup(pin_b, GPIO.OUT)

        self.pwm_a = GPIO.PWM(pin_a, 1000)
        self.pwm_b = GPIO.PWM(pin_b, 1000)

        self.target_speed = 0
        self.speed = 0
        self.pwm_a.start(0)
        self.pwm_b.start(0)

        thread = Thread(target=self.update_loop)
        thread.start()

    def update_loop(self):
        while True:
            if self.speed < self.target_speed:
                self.set_actual_speed(self.speed + 1)
            elif self.speed > self.target_speed:
                self.set_actual_speed(self.speed - 1)
            time.sleep(self.update_delay)

    def set_actual_speed(self, speed):
        self.speed = speed
        if speed >= 0:
            self.pwm_a.ChangeDutyCycle(speed)
            self.pwm_b.ChangeDutyCycle(0)
        else:
            self.pwm_a.ChangeDutyCycle(0)
            self.pwm_b.ChangeDutyCycle(-speed)

    def set_speed(self, speed):
        self.target_speed = speed

    def change_speed(self, speed_delta):
        self.target_speed += speed_delta

    def get_speed(self):
        return self.target_speed
