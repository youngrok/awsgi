import os
from setuptools import setup, find_packages


setup(name='expresspy',
      description='python version of express.js',
      author='Youngrok Pak',
      author_email='pak.youngrok@gmail.com',
      keywords= 'expressjs asyncio http server web',
      url='https://github.com/youngrok/awsgi',
      version='0.0.1',
      packages=find_packages(),
      classifiers = [
                     'Development Status :: 3 - Alpha',
                     'Topic :: Software Development :: Libraries',
                     'License :: OSI Approved :: BSD License']
      )
