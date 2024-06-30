#!/usr/bin/env python
from os.path import join

from setuptools import setup, find_packages

MODULE_NAME = 'crypto-dashboard'         # package name used to install via pip (as shown in `pip freeze` or `conda list`)
MODULE_NAME_IMPORT = 'crypto-dashboard'  # this is how this module is imported in Python (name of the folder inside `src`)
REPO_NAME = 'crypto-dashboard'           # repository name

def requirements_from_pip(filename='requirements.txt'):
    with open(filename, 'r') as pip:
        return [l.strip() for l in pip if not l.startswith('#') and l.strip()]

core_deps = requirements_from_pip()
# lgbm_deps = requirements_from_pip("requirements_lgbm.txt")


SETUP_ARGS = dict(name=MODULE_NAME,
      description="Crypto dashboards",
      long_description_content_type="text/markdown",
      url='https://github.com/diegoarri91/{:s}'.format(REPO_NAME),
      python_requires='>=3.8,<3.10',
      author="Diego M. Arribas",
      # package_dir={'': 'src'},
      packages=find_packages('./'),
      version="0.1.0",
      install_requires=core_deps,
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9'
          ])

if __name__ == "__main__":
    setup(**SETUP_ARGS)