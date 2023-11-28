from dataclasses import dataclass

import numpy


@dataclass
class CapturedFrame:
    frame: numpy.ndarray  # The captured frame
    frame_num: int  # The frame number
    read_time: float  # The time it took to read this frame
