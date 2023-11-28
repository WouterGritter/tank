import asyncio


class EmitQueue:
    def __init__(self, sio, timeout=0.001):
        self.sio = sio
        self.timeout = timeout

        self.queue = []

    def emit(self, name, data, sid):
        self.queue.append(FutureEmit(name, data, sid))

    def start_queue_worker(self, app):
        app.add_task(self.__queue_worker())

    async def __queue_worker(self):
        while True:
            await asyncio.sleep(self.timeout)

            while self.queue:
                future_emit = self.queue.pop()
                await future_emit.emit(self.sio)


class FutureEmit:
    def __init__(self, name, data, sid):
        self.name = name
        self.data = data
        self.sid = sid

    async def emit(self, sio):
        await sio.emit(
            self.name,
            self.data,
            self.sid
        )
