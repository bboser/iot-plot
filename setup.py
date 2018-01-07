from setuptools import setup
import os, sys

if sys.version_info < (3,4):
    print('iot_plot requires Python 3.4 or newer.')
    sys.exit(1)

setup(
  name = 'iot_plot',
  packages = ['iot_plot'],
  version = "0.3",
  description = 'Remote plotting library',
  license = 'MIT',
  author = 'Bernhard Boser',
  author_email = 'boser@berkeley.edu',
  url = 'https://github.com/bboser/iot-plot',
  download_url = 'https://github.com/bboser/iot-plot/archive/0.1.tar.gz',
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
      'matplotlib'
  ],
  entry_points = {
      'console_scripts': [
          'plotserver=iot_plot.plotserver:main',
          'plotclient=iot_plot.plotclient:main'
      ],
  },
)
