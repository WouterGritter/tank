import asyncio
import time
from typing import Optional

import socketio

from motor.motor import Motor
from motor.motor_factory import build_motors
from videostreamer.commandvideostreamer import CommandVideoStreamer

sio = socketio.AsyncClient()

motor_a: Optional[Motor] = None
motor_b: Optional[Motor] = None

last_classification_time = time.time()


async def websocket_thread(websocket_uri):
    while True:
        try:
            print(f'Attempting to connect to {websocket_uri}..')
            await sio.connect(websocket_uri)
            # This will keep the websocket connection alive
            await sio.wait()
        except Exception:
            print('Connection failed, retrying in a couple of seconds.')
            time.sleep(5)
            await asyncio.sleep(5)


@sio.event
async def connect():
    print('Connected to socket.io.')


@sio.event
async def disconnect():
    print('Disconnected from socket.io.')


def map(value, min, max, nmin, nmax):
    return (value - min) / (max - min) * (nmax - nmin) + nmin


@sio.on('ai_result')
async def handle_ai_result(data):
    global last_classification_time

    primary_classification = None
    for classification in data['classifications']:
        if classification['name'] in ['cat', 'dog', 'person']:
            primary_classification = classification
            break

    if primary_classification is None:
        if time.time() - last_classification_time > 5:
            motor_a.set_speed(30)
            motor_b.set_speed(-30)
        else:
            motor_a.set_speed(0)
            motor_b.set_speed(0)

        return

    last_classification_time = time.time()

    x = (primary_classification['x1'] + primary_classification['x2']) / 2.0
    if x < 0.4:
        print('Classification is on the LEFT.')
        speed = map(x, 0, 0.4, 50, 20)
        print(f'[L] {x=} {speed=}')
        motor_a.set_speed(-speed)
        motor_b.set_speed(speed)
    elif x > 0.6:
        print('Classification is on the RIGHT.')
        speed = map(x, 0.6, 1.0, 20, 50)
        print(f'[R] {x=} {speed=}')
        motor_a.set_speed(speed)
        motor_b.set_speed(-speed)
    else:
        print('Classification is in the CENTER.')
        motor_a.set_speed(50)
        motor_b.set_speed(50)


def main():
    global motor_a, motor_b
    motor_a, motor_b = build_motors()

    video_endpoint = 'udp://10.43.60.136:6969'
    video_command = f'libcamera-vid --flush -t 0 --inline --codec h264 --bitrate 3000000 --denoise cdn_off --level 4.2 --width 640 --height 480 --framerate 60 --mode 1640:1232:10 --nopreview --vflip --profile baseline -o {video_endpoint}'

    websocket_endpoint = 'http://10.43.60.136:8080'

    videostreamer = CommandVideoStreamer(video_command)
    videostreamer.begin()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([
        loop.create_task(websocket_thread(websocket_endpoint)),
    ]))
    loop.close()


if __name__ == '__main__':
    main()
