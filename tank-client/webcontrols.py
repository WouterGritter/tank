from typing import Optional

from flask import Flask, redirect

from motor.motor import Motor
from motor.motor_factory import build_motors

app = Flask(__name__, static_url_path='', static_folder='web')

motor_a: Optional[Motor] = None
motor_b: Optional[Motor] = None


@app.route('/')
def route_index():
    return redirect('/index.html')


@app.route('/update/<a_speed>/<b_speed>')
def route_test(a_speed, b_speed):
    a_speed = int(a_speed)
    b_speed = int(b_speed)

    motor_a.set_speed(a_speed)
    motor_b.set_speed(b_speed)

    return redirect('/index.html')


def main():
    global motor_a, motor_b
    motor_a, motor_b = build_motors()

    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
