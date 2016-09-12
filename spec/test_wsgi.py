import asyncio
import traceback
import unittest

import requests
from multiprocessing import Process

import websockets.client

from awsgi.server import serve
from sample import wsgiapp, asyncapp, websocketapp, wsgiupload


class WSGITest(unittest.TestCase):

    def test_plaintext(self):
        p = Process(target=serve, args=[wsgiapp.application], kwargs={'wsgi': True})
        p.start()
        self.assertEqual('Hello world!\n', requests.get('http://127.0.0.1:8000').text)
        p.terminate()
        p.join()

    def test_async(self):
        p = Process(target=serve, args=[asyncapp.application])
        p.start()
        self.assertEqual('Hello async!\n', requests.get('http://127.0.0.1:8000').text)
        p.terminate()
        p.join()

    def test_websocket(self):
        p = Process(target=serve, args=[websocketapp.application])
        p.start()

        loop = asyncio.get_event_loop()

        async def test_echo():
            async with websockets.client.connect('ws://localhost:8000/') as client:
                await client.send('Websocket Rocks!')
                self.assertEqual("Websocket Rocks!", await client.recv())

        loop.run_until_complete(test_echo())

        p.terminate()
        p.join()

    def test_upload(self):
        p = Process(target=serve, args=[wsgiupload.application])
        p.start()

        fails = 0
        for i in range(0, 10):
            res = requests.post('http://localhost:8000/',
                                files={'file': open('../sample/hearthstone-7level.png', 'rb')})

            with open('../sample/hearthstone-7level.png', 'rb') as f:
                try:
                    self.assertSequenceEqual(f.read(), res.content)
                except:
                    fails += 1

        print('fails', fails)
        p.terminate()
        p.join()
