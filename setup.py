from setuptools import setup

setup(
    name='discord-py-api',
    py_scipts=['data_over_audio'],
    version='0.3.0',
    description='A library for transmitting data over audio via frequency modulation.',
    author='Lett',
    install_requires=[
        'setuptools~=75.1.0',
        'pysine~=0.9.2',
        'numpy~=2.1.1',
        'sounddevice~=0.5.0',
        'scipy~=1.14.1'
    ],
)
