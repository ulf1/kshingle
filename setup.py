from setuptools import setup
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        s = fp.read()
    return s


def get_version(path):
    with open(path, "r") as fp:
        lines = fp.read()
    for line in lines.split("\n"):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(name='kshingle',
      version=get_version("kshingle/__init__.py"),
      description="Split strings into (character-based) k-shingles",
      long_description=read('README.rst'),
      url='http://github.com/ulf1/kshingle',
      author='Ulf Hamster',
      author_email='554c46@gmail.com',
      license='Apache License 2.0',
      packages=['kshingle'],
      install_requires=[
          'numpy>=1.19.0,<2',
          'numba>=0.52.0',
          'ray>=1.11.0,<2', 'protobuf<=3.20.*', 'psutil>=5.9.0,<6'
      ],
      python_requires='>=3.6',
      zip_safe=True)
