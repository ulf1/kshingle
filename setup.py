from setuptools import setup
import pypandoc


setup(name='kshingle',
      version='0.6.1',
      description="Split strings into (character-based) k-shingles",
      long_description=pypandoc.convert('README.md', 'rst'),
      url='http://github.com/ulf1/kshingle',
      author='Ulf Hamster',
      author_email='554c46@gmail.com',
      license='Apache License 2.0',
      packages=['kshingle'],
      install_requires=[
          'setuptools>=40.0.0',
          'numba>=0.52.0'
      ],
      python_requires='>=3.6',
      zip_safe=True)
