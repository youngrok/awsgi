import asyncio

import sys
from concurrent.futures.thread import ThreadPoolExecutor

import uvloop
from awsgi.server import serve, AsyncWSGIProtocol
from gunicorn.workers.async import AsyncWorker


class AwsgiWorker(AsyncWorker):

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        loop.set_default_executor(ThreadPoolExecutor(max_workers=1))

        servers = []
        for sock in self.sockets:
            server = loop.run_until_complete(
                loop.create_server(lambda: AsyncWSGIProtocol(self.wsgi, loop), sock=sock))
            servers.append(server)

        loop.call_later(1, self.start_notifying)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            print('server stopped')
            sys.exit(0)

        finally:
            for server in servers:
                server.close()

            loop.close()

    def start_notifying(self):
        asyncio.ensure_future(self.call_notify())

    async def call_notify(self):
        while True:
            self.notify()
            await asyncio.sleep(self.timeout)
