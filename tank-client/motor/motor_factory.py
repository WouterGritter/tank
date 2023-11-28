def build_motors():
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        return build_pi_motors()
    except:
        return build_dummy_motors()


def build_pi_motors():
    from motor.pi_motor import PiMotor

    a = PiMotor(13, 19)
    b = PiMotor(18, 12)
    return a, b


def build_dummy_motors():
    from motor.dummy_motor import DummyMotor

    a = DummyMotor()
    b = DummyMotor()
    return a, b
