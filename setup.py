from setuptools import setup, find_packages
setup(name = "redact-py",
        version = "0.1",
        packages=['redact'],
        install_requires=['redis==2.10.3'])
