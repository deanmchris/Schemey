from distutils.core import setup
from setuptools import find_packages


DESCRIPTION = '''\
Schemey is a suite for the Scheme language in written in pure Python'''


setup(
    name='Schemey',
    description=DESCRIPTION,
    author="Eli Bendersky",
    author_email="eliben@gmail.com",
    version='1.0.0',
    packages=find_packages(),
    license='PD',
    entry_points={
        'console_scripts': [
            'schemey = src.schemey:main',
        ],
    },
)
