from abc import abstractmethod


class VideoStreamer:
    @abstractmethod
    def begin(self):
        pass

    @abstractmethod
    def end(self):
        pass
