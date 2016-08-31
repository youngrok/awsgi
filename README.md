# aWSGI - Asynchronous WSGI server
aWSGI is an asynchronous WSGI server based on asyncio. It's designed to support both standard wsgi application and coroutine.

**DO NOT USE IN PRODUCTION**

## design goal
 * conform WSGI standard
 * support WSGI-like coroutine(async/await)
 * reliable start/stop/reload/restart
 * handle unix signals properly
 * manage multiprocess, multithread
 * connect nginx
 * reuse other open source as much as possible

## install
prerequisite

 * python >=3.5
 * uvloop
 * httptools

install with pip

	pip install awsgi
	
## usage
### command line
	
	python -m awsgi.server wsgi_file
	
