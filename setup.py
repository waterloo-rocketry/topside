from os import path

from setuptools import setup, find_packages

from topside import release_info

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=release_info.name,
    version=release_info.version,
    description=release_info.description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/waterloo-rocketry/topside',
    author='Waterloo Rocketry',
    author_email='contact@waterloorocketry.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
    ],
    packages=find_packages(exclude=['application']),
)
