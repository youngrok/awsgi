import os
from setuptools import setup, find_packages


setup(name='awsgi',
      description='asynchronous wsgi server',
      author='Youngrok Pak',
      author_email='pak.youngrok@gmail.com',
      keywords= 'asyncio http server wsgi',
      url='https://github.com/youngrok/awsgi',
      version='0.0.3',
      packages=find_packages(),
      install_requires=[
          'uvloop',
          'httptools',
          'websockets',
          'werkzeug',
      ],
      classifiers = [
                     'Development Status :: 3 - Alpha',
                     'Topic :: Software Development :: Libraries',
                     'License :: OSI Approved :: BSD License']
      )
