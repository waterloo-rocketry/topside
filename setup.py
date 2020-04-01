from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='operations_simulator',
    version='0.1.0',
    description='A simulator for rocket launch operations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/waterloo-rocketry/operations-simulator',
    author='Waterloo Rocketry',
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    package_dir={'': 'operations_simulator'},
    packages=find_packages(where='operations_simulator'),
)
