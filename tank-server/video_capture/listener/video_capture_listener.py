from abc import ABC, abstractmethod
from typing import Callable, Optional

import cv2

from video_capture.captured_frame import CapturedFrame


class VideoCaptureListener(ABC):
    @abstractmethod
    def on_stream_ready(self, video_capture: cv2.VideoCapture):
        pass

    @abstractmethod
    def on_stream_dispose(self):
        pass

    @abstractmethod
    def handle_frame(self, capture: CapturedFrame):
        pass


class LambdaVideoCaptureListener(VideoCaptureListener):
    def __init__(self,
                 stream_ready_callback: Optional[Callable[[], None]],
                 stream_dispose_callback: Optional[Callable[[], None]],
                 frame_callback: Optional[Callable[[CapturedFrame], None]]):
        self.stream_ready_callback = stream_ready_callback
        self.stream_dispose_callback = stream_dispose_callback
        self.frame_callback = frame_callback

    def on_stream_ready(self, video_capture: cv2.VideoCapture):
        if self.stream_ready_callback is not None:
            self.stream_ready_callback()

    def on_stream_dispose(self):
        if self.stream_dispose_callback is not None:
            self.stream_dispose_callback()

    def handle_frame(self, capture: CapturedFrame):
        if self.frame_callback is not None:
            self.frame_callback(capture)
