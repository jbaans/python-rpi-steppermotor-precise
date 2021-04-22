#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'pigpio>=1',
]

tests_require = []

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='python-rpi-steppermotor-precise',
    version='1.0',
    author='JB Aans',
    author_email='jbaans-at-gmail.com',
    license='GPL',
    url='https://github.com/jbaans/python-rpi-steppermotor-precise',
    packages=find_packages(),
    description='Advanced stepper motor interface',
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url='https://github.com/jbaans/python-rpi-steppermotor-precise/archive/master.zip',
    keywords=['raspberry', 'pi', 'gpio', 'pigpio', 'precise', 'PWM', 'A4988',
              'DRV8825', 'stepper', 'motor', 'driver', 'interface', 'wrapper'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Automation Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Scientific/Engineering'
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
