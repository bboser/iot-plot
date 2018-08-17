from setuptools import setup
import sys

if sys.version_info < (3,4):
    print('iot_plot requires Python 3.6 or newer.')
    sys.exit(1)

setup(
  name = 'iot-plot',
  packages = ['lib'],
  version = "0.6.7",
  description = 'Remote plotting library',
  long_description = 'See documentation at https://github.com/bboser/iot-plot',
  license = 'MIT',
  author = 'Bernhard Boser',
  author_email = 'boser@berkeley.edu',
  url = 'https://github.com/bboser/iot-plot',
  keywords = ['plotting', 'micropython', 'MQTT'],
  classifiers = [
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Embedded Systems',
      'Topic :: Utilities',
  ],
  install_requires=[
      'matplotlib',
      'paho-mqtt'
  ],
  entry_points = {
      'console_scripts': [
          'plotserver=lib.plotserver:main',
          'plotclient=lib.plotclient:main'
      ],
  },
)
