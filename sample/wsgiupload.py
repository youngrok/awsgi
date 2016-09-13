import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from werkzeug.formparser import parse_form_data

import awsgi.wsgi


@awsgi.wsgi.adapter
def application(environ, start_response):
    response_headers = [('Content-type', 'application/octet-stream')]
    stream, form, files = parse_form_data(environ)
    stream, form, files = parse_form_data(environ)

    try:
        start_response('200 OK', response_headers)
        return files['file'].stream
    except:
        start_response('400 BAD REQUEST', response_headers)
        return [environ['PATH_INFO']]

