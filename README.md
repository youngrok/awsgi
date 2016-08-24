# aWSGI - Asynchronous WSGI server
aWSGI is an asynchronous WSGI server based on asyncio. It's designed to support both standard wsgi application and coroutine.

## design goal
 * conform WSGI standard
 * support WSGI-like coroutine(async/await)
 * reliable start/stop/reload/restart
 * handle unix signals
 * manage multiprocess, multithread
 * connect nginx

## install

	pip install awsgi

## usage
### command line
	
	awsgi wsgi_file
	
### systemd
	
	systemctl start awsgi
	
