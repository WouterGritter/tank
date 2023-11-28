import time
from queue import Queue
from threading import Thread
from typing import Optional

import cv2

from video_capture.captured_frame import CapturedFrame
from video_capture.listener.video_capture_listener import VideoCaptureListener


class AsyncVideoCaptureListenerWrapper(VideoCaptureListener):
    def __init__(self, listener: VideoCaptureListener):
        self.listener = listener
        self.running = False

        self.thread: Optional[Thread] = None
        self.queue: Optional[Queue] = None

        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.fps_dropped_counter = 0

    def on_stream_ready(self, video_capture: cv2.VideoCapture):
        assert not self.running

        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.fps_dropped_counter = 0

        self.queue = Queue()

        self.running = True
        self.thread = Thread(target=self.__frame_worker)
        self.thread.daemon = True
        self.thread.start()

        self.listener.on_stream_ready(video_capture)

    def on_stream_dispose(self):
        assert self.running

        self.running = False
        self.thread.join()

        self.thread = None
        self.queue = None

        self.listener.on_stream_dispose()

    def handle_frame(self, capture: CapturedFrame):
        if not self.queue.empty():
            self.queue.get_nowait()
            self.fps_dropped_counter += 1

        self.queue.put(capture)

    def __frame_worker(self):
        assert self.running

        print(f'[{self.listener.__class__.__name__}] frame_worker thread started.')
        while self.running:
            try:
                # Timeout and raises an exception after 1 second. This gives it a chance
                # to check the self.running variable again.
                capture = self.queue.get(block=True, timeout=1)
            except Exception:
                continue

            self.listener.handle_frame(capture)

            self.fps_counter += 1
            now = time.time()
            if now - self.fps_start_time >= 10:
                fps = self.fps_counter / (now - self.fps_start_time)
                dfps = self.fps_dropped_counter / (now - self.fps_start_time)
                print(f'[{self.listener.__class__.__name__}] Total fps: {fps + dfps:.2f}, fps: {fps:.2f}, dropped fps: {dfps:.2f}')

                self.fps_start_time = now
                self.fps_counter = 0
                self.fps_dropped_counter = 0

        print(f'[{self.listener.__class__.__name__}] frame_worker thread exited.')
