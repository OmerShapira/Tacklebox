# Setup.py

from setuptools import setup
from src.consts import consts

setup(name='tacklebox',
      version=consts.VERSION,
      description='portable configuration manager',
      url='http://github.com/OmerShapira/Tacklebox',
      author='Omer Shapira',
      author_email='info@omershapira.com',
      license='MIT',
      packages=['tacklebox'],
      install_requires=[
          'toml',
          'GitPython'
      ],
      zip_safe=False)
