import argparse
import asyncio
import io
import socket
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from importlib import machinery

import httptools
import sys

import uvloop
from httptools.parser.errors import HttpParserUpgrade
from werkzeug.urls import url_parse, url_unquote

from awsgi.blockingio import BlockingIO
from awsgi.wsgi import adapter


class AsyncWSGIProtocol(asyncio.Protocol):

    def __init__(self, application, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.request = None
        self.parser = httptools.HttpRequestParser(self)
        self.application = application
        self.headers = {}
        self.path = None
        self.buffer = BlockingIO()
        self.content_length = 0
        self.closed = False
        self.upgraded_protocol = None
        self.body_read_pos = 0

    def connection_made(self, transport):
        self.transport = transport
        sock = transport.get_extra_info('socket')
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except (OSError, NameError):
            pass

    def data_received(self, data):

        if self.upgraded_protocol:
            self.upgraded_protocol.data_received(data)
            return

        try:
            self.parser.feed_data(data)
        except HttpParserUpgrade as e:
            '''
            let framework handle protocol upgrade
            '''
            pass

    def on_header(self, name, value):
        try:
            self.headers[name.decode('utf8')] = value.decode('utf8')
        except:
            traceback.print_exc()

    def on_headers_complete(self):
        asyncio.ensure_future(self.async_process_response(), loop=self.loop)

    def on_url(self, url):
        self.path = url

    def on_body(self, data):
        self.buffer.feed_data(data)

    def on_message_complete(self):
        self.buffer.feed_eof()

    def connection_lost(self, exc):
        self.closed = True
        if self.upgraded_protocol:
            self.upgraded_protocol.connection_lost(exc)

    def eof_received(self):
        self.buffer.feed_eof()

    async def async_process_response(self):
        try:
            it = await self.application(self.make_environ(), self.start_response)
            self.write(b'\r\n')
            for data in it:
                self.write(data)

            # self.transport.write('Content-Length: {}\r\n'.format(len(b)).encode('utf8'))
            self.write_eof()
        except:
            traceback.print_exc()
            self.write_eof()

    def write(self, data):
        self.transport.write(data)
        print('write', data)

    def write_eof(self):
        if not self.closed and not self.upgraded_protocol:
            self.transport.write_eof()

    def start_response(self, status, response_headers):
        self.write('HTTP/1.1 {}\r\n'.format(status).encode('utf8'))
        for header in response_headers:
            if header[0].lower() == 'content-length':
                self.content_length = header[1]

            if header[0].lower() == 'connection' and header[1].lower() == 'upgrade':
                assert self.upgraded_protocol

            self.write('{0}: {1}\r\n'.format(header[0], header[1]).encode('utf8'))

    def make_environ(self):
        request_url = url_parse(self.path)

        # url_scheme = self.server.ssl_context is None and 'http' or 'https'
        path_info = url_unquote(request_url.path)

        environ = {
            'awsgi.upgrade': self.upgrade,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': self.buffer,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': True,
            'REQUEST_METHOD': self.parser.get_method().decode('utf8'),
            'SCRIPT_NAME': '',
            'PATH_INFO': path_info,
            'QUERY_STRING': request_url.query.decode('utf8'),
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': self.headers.get('Content-Length', ''),
            'REMOTE_ADDR': self.transport.get_extra_info('socket').getpeername()[0],
            'REMOTE_PORT': self.transport.get_extra_info('socket').getpeername()[1],
            'SERVER_NAME': self.transport.get_extra_info('socket').getsockname()[0],
            'SERVER_PORT': self.transport.get_extra_info('socket').getsockname()[1],
            'SERVER_PROTOCOL': ''
        }

        for key, value in self.headers.items():
            key = 'HTTP_' + key.upper().replace('-', '_')
            if key not in ('HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH'):
                environ[key] = value

        if request_url.scheme and request_url.netloc:
            environ['HTTP_HOST'] = request_url.netloc

        return environ

    def upgrade(self, websocket_protocol):
        self.upgraded_protocol = websocket_protocol(self.loop)
        self.upgraded_protocol.connection_made(self.transport)
        return self.upgraded_protocol


def serve(application, host='127.0.0.1', port=8000, threads=1, wsgi=False, loop=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = loop or asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_default_executor(ThreadPoolExecutor(max_workers=threads))
    if wsgi:
        application = adapter(application)

    server = loop.run_until_complete(
        loop.create_server(lambda: AsyncWSGIProtocol(application, loop), host=host, port=port))
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
