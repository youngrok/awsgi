import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from werkzeug.formparser import parse_form_data

import awsgi.wsgi


@awsgi.wsgi.adapter
def application(environ, start_response):
    response_headers = [('Content-type', 'application/octet-stream')]
    start_response('200 OK', response_headers)
    stream, form, files = parse_form_data(environ)

    return files['file'].stream
