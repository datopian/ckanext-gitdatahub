# ckanext-gitdatahub

A CKAN extension to write Dataset and Resources's metadata into a git-backed backend. It stores the metadata in a datapackage.json using the frictionless data format. So far the extension uses GitHub as a git-backed backend with support for `git-lfs` but in the future will provide support for different services (like Gitlab).

For a glimpse on how a GitHub repository will look like to store metadata information using frictionless data standards checkout: [https://github.com/datasets/](https://github.com/datasets/)

## Requirements

This extension has been tested and developed using CKAN 2.8.3

## Installation

To install ckanext-gitdatahub:

1. Activate your CKAN virtual environment, for example
     `. /usr/lib/ckan/default/bin/activate`

2. Install the ckanext-gitdatahub Python package into your virtual environment:

     `pip install ckanext-gitdatahub`

3. Add `gitdatahub_package gitdatahub_resource` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/production.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     `sudo service apache2 reload`

## Config Settings

#### ckanext.gitdatahub.access_token

API Key to access a Github.


## Development Installation

To install ckanext-gitdatahub for development, activate your CKAN virtualenv and
do:

```
git clone https://github.com/pdelboca/ckanext-gitdatahub.git
cd ckanext-gitdatahub
python setup.py develop
pip install -r dev-requirements.txt
```


## Running the Tests

To run the tests, do:

`nosetests --nologcapture --with-pylons=test.ini`

To run the tests and produce a coverage report, first make sure you have coverage installed in your virtualenv (``pip install coverage``) then run:

`nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.gitdatahub --cover-inclusive --cover-erase --cover-tests`



## Registering ckanext-gitdatahub on PyPI


ckanext-gitdatahub should be availabe on PyPI as https://pypi.python.org/pypi/ckanext-gitdatahub. If that link doesn't work, then
you can register the project on PyPI for the first time by following these steps:

1. Create a source distribution of the project:

    `python setup.py sdist`

2. Register the project:

    `python setup.py register`

3. Upload the source distribution to PyPI:

    `python setup.py sdist upload`

4. Tag the first release of the project on GitHub with the version number from the ``setup.py`` file. For example if the version number in ``setup.py`` is 0.0.1 then do:
```
git tag 0.0.1
git push --tags
```


## Releasing a New Version of ckanext-gitdatahub

ckanext-gitdatahub is availabe on PyPI as https://pypi.python.org/pypi/ckanext-gitdatahub.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Create a source distribution of the new version:

    `python setup.py sdist`

3. Upload the source distribution to PyPI:

    `python setup.py sdist upload`

4. Tag the new release of the project on GitHub with the version number from the `setup.py` file. For example if the version number in `setup.py` is 0.0.2 then do:

```
git tag 0.0.2
git push --tags
```