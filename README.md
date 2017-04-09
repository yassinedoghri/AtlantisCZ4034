# Donald Tweets v0.1.0
A project that aims to detect sarcasm in Govt. planning and decision (Trump's immigration order) tweets.

## Table of contents

* [Getting Started](#getting-started)
* [Structure](#structure)
* [User interface](#user-interface)
* [Versioning](#versioning)
* [Contributors](#contributors)
* [Copyright and licence](#copyright-and-licence)


## Getting Started

1. [Install Bower](http://bower.io/#install-bower)
2. Open command line
3. Go to project root folder
4. Run the following command to install project dependencies:

```sh
$ bower install
```

4. [Setup virtualenv](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/)
5. Run the following command to install project python libraries:

```sh
$ pip install -r requirements/requirements.txt
```

6. [Install](https://docs.mongodb.com/manual/installation/) & [Run](https://docs.mongodb.com/manual/tutorial/manage-mongodb-processes/) MongoDB
7. [Install](https://www.elastic.co/guide/en/elasticsearch/reference/1.7/_installation.html) & [Run](https://www.elastic.co/guide/en/elasticsearch/guide/1.x/running-elasticsearch.html) Elasticsearch
8. Set access keys for the Twitter API in `app/mining.py`

```python
TWEEPY_CONSUMER_KEY = 'your_consumer_key'
TWEEPY_CONSUMER_SECRET = 'your_consumer_secret'
TWEEPY_ACCESS_TOKEN_KEY = 'your_access_token'
TWEEPY_ACCESS_TOKEN_SECRET = 'your_access_token_secret'
```

9. Run the following scripts in order:

```sh
# Activate the virtual environment
$ source venv/bin/activate

# run the scripts one by one
$ python app/mining.py
$ python app/parsing.py
$ python app/indexing.py
```

10. Run the Flask App:

```sh
# Make sure the virtualenv is activated
$ python autoapp.py
```

## Structure

The structure of Donald Tweets has been generated using [cookiecutter-flask](https://github.com/sloria/cookiecutter-flask), a template for [cookiecutter](https://github.com/audreyr/cookiecutter).

## User interface

The UI of Atlantis CMS is built using [Materializecss](http://materializecss.com/).

## Versioning

Donald Tweets is maintained under the [Semantic Versioning guidelines](http://semver.org/).

## Contributors

This project is a school project for the CZ4034 module at the Nanyang Technological University (NTU) of Singapore.

### Student

- [Yassine Doghri](https://github.com/yassinedoghri)

## Copyright and licence

// TO DO - Project licence.
