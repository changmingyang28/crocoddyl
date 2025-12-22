from setuptools import find_packages
from setuptools import setup

setup(
    name='wbot_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('wbot_msgs', 'wbot_msgs.*')),
)
