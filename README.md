# aWSGI - Asynchronous WSGI server
aWSGI is an asynchronous WSGI server based on asyncio. It's designed to support both standard wsgi application and coroutine.

**DO NOT USE IN PRODUCTION**

## design goal
 * conform WSGI standard
 * support WSGI-like coroutine(async/await)
 * reliable start/stop/reload/restart
 * handle unix signals
 * manage multiprocess, multithread
 * connect nginx

## install
prerequisite

 * python >=3.5
 * uvloop
 * httptools

install for development

	git clone git@github.com:youngrok/awsgi.git
	cd awsgi
	python setup.py develop
	
awsgi cannot be installed with PyPI because it's status is not production ready.

## usage
### command line
	
	python -m awsgi.server wsgi_file
	
