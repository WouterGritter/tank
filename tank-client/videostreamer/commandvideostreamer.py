import subprocess
from threading import Thread

from videostreamer.videostreamer import VideoStreamer


class CommandVideoStreamer(VideoStreamer):
    def __init__(self, command):
        self.process = None
        self.process_thread = None
        self.command = command

    def begin(self):
        self.end()

        self.process_thread = Thread(target=self.__process_thread)
        self.process_thread.daemon = True
        self.process_thread.start()

    def end(self):
        if self.process is None:
            return

        self.process.terminate()
        self.process = None

        self.process_thread.join()
        self.process_thread = None

        print('Ended external video stream process.')

    def __process_thread(self):
        print(f'Starting external video stream process with command {self.command}')
        self.process = subprocess.Popen(self.command.split(' '), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self.process.wait()
