from setuptools import setup, find_packages
import os

# Get the version info we do this to avoid importing __init__, which
# depends on other packages that may not yet be installed.
base_dir = os.path.abspath(os.path.dirname(__file__))
version = {}
with open(base_dir + "/cmist/_version.py") as fp:
    exec(fp.read(), version)


config = dict(
    name='cmist-lib',
    version=version['__version__'],
    description='A library for accessing data in the NOAA cmist webpage',
    author='Levi Kilcher',
    author_email='Levi.Kilcher@nrel.gov',
    classifiers=[
        'Development Status :: 5 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
    ],
    url='http://github.com/lkilcher/cmist',
    packages=find_packages(),
    # ['dolfyn', 'dolfyn.adv', 'dolfyn.io', 'dolfyn.data',
    #           'dolfyn.rotate', 'dolfyn.tools', 'dolfyn.adp', ],
    package_data={'': ['data/coops_stations.json']},
    include_package_data=True,
    install_requires=['scipy', 'xarray', 'selenium', 'pandas'],
    provides=['cmist', ],
)

setup(**config)
