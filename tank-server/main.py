import math
from typing import Any

import cv2
import socketio
import torch
from sanic import Sanic

from emit_queue import EmitQueue
from video_capture.captured_frame import CapturedFrame
from video_capture.listener.async_video_capture_listener_wrapper import AsyncVideoCaptureListenerWrapper
from video_capture.listener.video_capture_listener import LambdaVideoCaptureListener
from video_capture.video_capture import VideoCapture

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic("Server")
sio.attach(app)

emit_queue = EmitQueue(sio)

model: Any = None
connected_client: Any = None


@sio.event
async def connect(sid, environ):
    global connected_client

    if connected_client is not None:
        print('WARNING! A client tried to connect, but another client is already connected.')
        await sio.disconnect(sid)
        return

    print(f'A new client has connected. SID: {sid}.')
    connected_client = sid


@sio.event
async def disconnect(sid):
    global connected_client

    if connected_client is None or connected_client != sid:
        print('WARNING! Ignoring disconnect from wrong client.')
        return

    print(f'Client disconnected. SID: {sid}')
    connected_client = None


def on_stream_ready():
    print('Stream is now ready.')


def on_stream_disposed():
    print('Stream is now disposed.')


def process_frame(frame: CapturedFrame):
    height, width = frame.frame.shape[:2]
    panda = model(frame.frame).pandas().xyxy[0]

    classifications = []
    for index, row in panda.iterrows():
        classifications.append({
            'name': row['name'],
            'confidence': row['confidence'],
            'x1': row['xmin'] / width,
            'y1': row['ymin'] / height,
            'x2': row['xmax'] / width,
            'y2': row['ymax'] / height,
        })

    return {
        'width': width,
        'height': height,
        'frame_num': frame.frame_num,
        'read_time': frame.read_time,
        'classifications': classifications,
    }


def add_bounding_boxes(frame, classifications):
    frame = frame.copy()
    height, width = frame.shape[:2]

    for res in classifications:
        x1 = math.floor(res['x1'] * width)
        y1 = math.floor(res['y1'] * height)
        x2 = math.floor(res['x2'] * width)
        y2 = math.floor(res['y2'] * height)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f'{res["name"]}-{res["confidence"] * 100:.1f}%',
            (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )

    return frame


def handle_frame(frame: CapturedFrame):
    if connected_client is None:
        print('WARNING! Ignoring frame while no socket.io client is connected.')
        return

    print('Received frame.')

    data = process_frame(frame)
    if connected_client is None:
        return  # Processing the frame takes some time, the client can disconnect in that time

    emit_queue.emit('ai_result', data, connected_client)

    frame_bb = add_bounding_boxes(frame.frame, data['classifications'])
    cv2.imshow("video", frame_bb)
    cv2.waitKey(1)


def main():
    global model

    print('Loading YOLO model...')
    model = torch.hub.load('WongKinYiu/yolov7', 'custom', 'yolov7.pt')
    model.to(torch.device('cuda:0'))
    print('YOLO model loaded.')

    video_capture = VideoCapture(
        listening_port=6969,
        listener=AsyncVideoCaptureListenerWrapper(
            LambdaVideoCaptureListener(
                stream_ready_callback=on_stream_ready,
                stream_dispose_callback=on_stream_disposed,
                frame_callback=handle_frame,
            ),
        ),
    )

    video_capture.start()

    emit_queue.start_queue_worker(app)
    app.run(
        host="0.0.0.0",
        port=8080,
    )


if __name__ == '__main__':
    main()
