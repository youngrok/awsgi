import asyncio
import asyncio.queues
import logging

from websockets.exceptions import (PayloadTooBig,
                         WebSocketProtocolError)
from websockets.protocol import WebSocketCommonProtocol

logger = logging.getLogger(__name__)


class WebSocketProtocol(WebSocketCommonProtocol):

    async def run(self):
        # This coroutine guarantees that the connection is closed at exit.
        await self.opening_handshake
        while not self.closing_handshake.done():
            try:
                msg = await self.read_message()
                if msg is None:
                    break
                await self.messages.put(msg)
                await self.message_received(await self.messages.get())

            except asyncio.CancelledError:
                break
            except WebSocketProtocolError:
                await self.fail_connection(1002)
            except asyncio.IncompleteReadError:
                await self.fail_connection(1006)
            except UnicodeDecodeError:
                await self.fail_connection(1007)
            except PayloadTooBig:
                await self.fail_connection(1009)
            except Exception:
                await self.fail_connection(1011)
                raise
        await self.close_connection()

    async def message_received(self, message):
        raise NotImplementedError