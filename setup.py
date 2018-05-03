from setuptools import setup, find_packages

setup(name='pycontrolsystem',
      version='1.0.0',
      description='A control system with QT-based Client and Server to control hardware (e.g. Arduino).',
      url='https://github.com/DanielWinklehner/pycontrolsystem',
      author='Thomas Wester, Daniel Winklehner',
      author_email='winklehn@mit.edu',
      license='MIT',
      packages=find_packages(),
      # package_data={'': ['mainwindow.py', 'propertieswindow.py']},
      include_package_data=True,
      zip_safe=False)
