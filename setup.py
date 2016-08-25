import os
from setuptools import setup, find_packages


setup(name='awsgi',
      description='asynchronous wsgi server',
      author='Youngrok Pak',
      author_email='pak.youngrok@gmail.com',
      keywords= 'asyncio http server wsgi',
      url='https://github.com/youngrok/awsgi',
      version='0.0.1',
      packages=find_packages(),
      classifiers = [
                     'Development Status :: 3 - Alpha',
                     'Topic :: Software Development :: Libraries',
                     'License :: OSI Approved :: BSD License']
      )
