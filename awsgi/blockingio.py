class BlockingIO:

    def __init__(self):
        self.queue = []
        self.got_eof = False

    def feed_data(self, data):
        self.queue.append(data)

    def read(self, size=-1):
        if size == -1 or not size:
            return self.readall()

        buffer = bytearray()

        while True:

            if not self.queue:
                if self.got_eof:
                    return bytes(buffer)

                continue

            buffer.extend(self.queue[0])
            del self.queue[0]

            if len(buffer) >= size:
                remaining = buffer[size:]
                if remaining:
                    self.queue.insert(0, remaining)

                return bytes(buffer[:size])

    def readall(self):
        buffer = bytearray()
        while self.queue or not self.got_eof:
            if not self.queue:
                continue

            buffer.extend(self.queue[0])
            del self.queue[0]

        return bytes(buffer)

    def readline(self):
        buffer = bytearray()

        while True:
            if not self.queue:
                if self.got_eof:
                    return bytes(buffer)

                continue

            cr_pos = self.queue[0].find(b'\n')
            if cr_pos < 0:
                buffer.extend(self.queue[0])
                del self.queue[0]
            else:
                buffer.extend(self.queue[0][:cr_pos])
                del self.queue[0][:cr_pos]
                return bytes(buffer)


    def feed_eof(self):
        self.got_eof = True
