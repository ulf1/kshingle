from setuptools import setup


def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='template_pypi',
      version='0.1.0',
      description='lorem ipsum',
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      url='http://github.com/myorg/template_pypi',
      author='John Doe',
      author_email='554c46@gmail.com',
      license='MIT',
      packages=['template_pypi'],
      install_requires=[
          'setuptools>=40.0.0'],
      python_requires='>=3.8',
      zip_safe=False)
