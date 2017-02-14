from concurrent.futures.process import ProcessPoolExecutor
import argparse
import asyncio
import logging
from importlib import machinery
from multiprocessing import pool, Process
from multiprocessing.pool import Pool

import sys
import uvloop

import awsgi
from awsgi import server

logger = logging.getLogger(__file__)


class ProxyProtocol(asyncio.Protocol):

    def __init__(self, host, port, loop):

        self.index = 0
        self.host = host
        self.port = port
        self.loop = loop
        self.client_reader = None
        self.client_writer = None

    def connection_made(self, transport):
        self.transport = transport
        asyncio.set_event_loop(self.loop)

    async def relay_data(self, data):
        if not self.client_reader:
            self.client_reader, self.client_writer = await asyncio.open_connection(self.host, self.port + self.index + 1)
            print('connect subprocess', self.port + self.index + 1)
            self.index = (self.index + 1) % 1
            self.client_writer.write(data)

            while True:
                print('polling...')
                if self.client_reader.at_eof():
                    self.transport.write_eof()
                    print('eof')
                    return

                print('not eof')
                response_data = await self.client_reader.read()
                print('res', response_data)
                self.transport.write(response_data)
        else:
            self.client_writer.write(data)

    def data_received(self, data):
        print('req', data)
        asyncio.ensure_future(self.relay_data(data))

    def connection_lost(self, exc):
        self.client_writer.close()


class ForkServer:

    def __init__(self, application, host, port, threads, wsgi, loop):
        self.application = application
        self.host = host
        self.port = port
        self.threads = threads
        self.wsgi = wsgi
        self.loop = loop

    def __call__(self):
        return server.serve(self.application, self.host, self.port, self.threads, self.wsgi, self.loop)


def serve(application, host='127.0.0.1', port=8000, threads=1, wsgi=False, loop=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = loop or asyncio.new_event_loop()

    for i in range(0, 1):
        p = Process(target=awsgi.server.serve, args=[application, host, port + i + 1, threads, wsgi, None])
        p.start()

    server = loop.run_until_complete(
        loop.create_server(lambda: ProxyProtocol(host, port, loop), host=host, port=port))

    print('aWSGI server started at http://{0}:{1}/'.format(*server.sockets[0].getsockname()))
    print('{} threads working.'.format(threads))
    print('Quit server with {}'.format('CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'))

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        print('server stopped')
        sys.exit(0)

    finally:
        server.close()
        loop.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='aWSGI server')
    parser.add_argument('awsgifile', metavar='<awsgi file>',
                        help='awsgi file that contains application coroutine')
    parser.add_argument('--host', metavar='host', default='127.0.0.1',
                        help='host to listen. default: 127.0.0.1')
    parser.add_argument('--port', metavar='port', default=8000, type=int,
                        help='port to listen. default: 8000')
    parser.add_argument('--threads', metavar='threads', default=1, type=int,
                        help='number of threads. default: 1')
    parser.add_argument('--wsgi', metavar='wsgi', default=False, type=bool,
                        help='WSGI compliant mode')

    args = parser.parse_args()

    awsgi_module = machinery.SourceFileLoader('awsgi', args.awsgifile).load_module()

    serve(awsgi_module.application, host=args.host, port=args.port, threads=args.threads, wsgi=args.wsgi)
