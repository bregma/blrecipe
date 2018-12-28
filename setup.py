#!/usr/bin/python3
from distutils import log
from setuptools import setup, find_packages, Command
import setuptools.command.test
import subprocess
import os


class TestCommand(setuptools.command.test.test):
    """
    Helper for unit testing discovery.
    """

    def _test_args(self):
        yield 'discover'
        for arg in super()._test_args():
            yield arg


class PylintCommand(Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run Pylint on Python source files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        command = ['/usr/bin/pylint3']
        command.append(os.path.join(os.getcwd(), 'blrecipe'))
        command.append(os.path.join(os.getcwd(), 'tests', 'unit'))
        self.announce('Running command: {}'.format(command), level=log.INFO)
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as ex:
            self.announce("command returned status {}".format(ex.args[0]), level=log.WARN)


setup(
    name='blrecipe',
    version='1.0',
    author='Stephen M. Webb',
    author_email='stephen.webb@bregmasoft.ca',
    packages=find_packages(),

    package_data={
        '': ['app/templates/*.html', 'app/static/css/*.css', 'app/static/js/*.js'],
    },

    # Platform-independent command-line drivers
    entry_points={
        'console_scripts': [
            'blrecipe-service = blrecipe.restapi.service:main',
            'blrecipe-app = blrecipe.app.__main__:main',
            'blrecipe = blrecipe.clt.__main__:main',
        ]
    },

    # Unit tests
    cmdclass={
        'test': TestCommand,
        'lint': PylintCommand,
    },
    test_suite='tests',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.7',
        'Framework :: Flask',
        'Environment :: Console',
        'Environment :: Web Environment',
    ]
)
