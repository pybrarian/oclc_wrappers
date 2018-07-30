[![Build Status](https://travis-ci.org/pybrarian/oclc_wrappers.svg?branch=master)](https://travis-ci.org/pybrarian/oclc_wrappers)
[![PyPI version](https://badge.fury.io/py/oclc-wrappers.svg)](https://badge.fury.io/py/oclc-wrappers)
## OCLC Wrappers

A set of wrappers to ease working with OCLC Web Services. Development has been mostly driven by the needs of Westfield
Stae's acquisitions program.

### Install
Easiest install is:
`pip install oclc-wrappers`

### Adding
The general flow is functions that return an object allowing you to do some type of work with OCLC resources. 
To add new endpoints, add the URLs and HTTP Verbs to a dict with the actions OCLC lists as keys, (i.e. 'create') 
and a namedtuple provided in constants.py of URL (with unknown url params in curly brackets {} for formatting) and HTTP Verb.
Then you should be able to write a function that takes an authorization object and the action you wish to take,
set up a Requestor object with the URLs you added, and go to town.

## TODO:
* Blog post to show the flow of adding new functionality
* Auth currently only implements HMAC and WSKey Lite, add Access Token
* Better document the whole library