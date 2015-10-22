import sys

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


from setuptools import setup, find_packages
setup(name = "redact-py",
        version = "0.1",
	tests_require=['pytest'],
	cmdclass = {'test': PyTest},
        packages=['redact'],
        install_requires=['redis==2.10.3'])
