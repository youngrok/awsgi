import io


class BlockingIO(io.BytesIO):

    timeout = 1

    def __init__(self, initial_bytes=None):
        super().__init__(initial_bytes)
        self.got_eof = False
        self.read_pos = 0

    def readline(self, size=-1):
        self.seek(self.read_pos)

        result = b''
        while not result:
            result = super().readline(size)

            if self.got_eof:
                return result

        self.read_pos += len(result)

        return result

    def read(self, size=-1):
        self.seek(self.read_pos)

        result = b''
        while not result:
            result = super().read(size)

            if self.got_eof:
                return result

        self.read_pos += len(result)

        return result

    def feed_eof(self):
        self.got_eof = True