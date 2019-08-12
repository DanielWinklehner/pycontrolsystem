from setuptools import setup, find_packages

setup(name='pycontrolsystem',
      version='1.0.2',
      python_requires='>=3',
      description='A control system with QT-based Client and Server to control hardware (e.g. Arduino).',
      url='https://github.com/DanielWinklehner/pycontrolsystem',
      author='Thomas Wester, Daniel Winklehner',
      author_email='winklehn@mit.edu',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
