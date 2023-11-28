import os
import time
from threading import Thread

import cv2

from video_capture.captured_frame import CapturedFrame
from video_capture.listener.video_capture_listener import VideoCaptureListener


# https://stackoverflow.com/questions/43665208/how-to-get-the-latest-frame-from-capture-device-camera-in-opencv
class VideoCapture:
    def __init__(self, listening_port: int, listener: VideoCaptureListener):
        self.listening_port = listening_port
        self.listener = listener

        self.running = False
        self.should_reset = False
        self.video_capture: cv2.VideoCapture = None

    def start(self):
        assert not self.running

        self.running = True

        reader_thread = Thread(target=self._reader_worker)
        reader_thread.daemon = True
        reader_thread.start()

    def abort(self):
        assert self.running

        self.running = False

    def reset(self):
        assert self.running

        self.should_reset = True

    def _reader_worker(self):
        assert self.running

        print(f'[VideoCapture] Opening UDP stream on port {self.listening_port}...')

        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'fflags;nobuffer|flags;low_delay|framedrop'
        self.video_capture = cv2.VideoCapture(f'udp://@:{self.listening_port}', cv2.CAP_FFMPEG)

        handled_first_frame = False
        frame_counter = 0

        while self.running:
            if self.should_reset:
                print('[VideoCapture] Resetting videostream...')
                self.should_reset = False
                break

            read_start = time.time()
            ret, frame = self.video_capture.read()
            read_elapsed = time.time() - read_start

            if not ret:
                break

            # Check twice because video_capture.read() can block for a long time
            if self.should_reset:
                print('[VideoCapture] Resetting videostream...')
                self.should_reset = False
                break

            if not handled_first_frame:
                handled_first_frame = True
                self.listener.on_stream_ready(self.video_capture)

            frame_counter += 1
            self.listener.handle_frame(CapturedFrame(frame, frame_counter, read_elapsed))

        print(f'[VideoCapture] UDP stream stopped on port {self.listening_port}...')
        self.video_capture.release()

        # Only call on_stream_dispose() if the first frame has been handled, eg. if on_stream_ready() has also been called
        if handled_first_frame:
            self.listener.on_stream_dispose()

        if self.running:
            # We should still be running, but the while loop exited (probably due to a bad connection).
            # Re-run this thread to attempt to reconnect.
            print('Re-running VideoCapture thread...')
            time.sleep(1.0)
            self._reader_worker()
