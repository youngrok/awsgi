import asyncio


def adapter(wsgi_application):

    async def application(environ, start_response):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, wsgi_application, environ, start_response)

    return application