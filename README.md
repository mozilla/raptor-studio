[![license](https://img.shields.io/badge/license-MPL%202.0-blue.svg)](https://github.com/davehunt/raptor-studio/blob/master/LICENSE.txt)
[![style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Raptor Studio

A simple command line tool for recording and replaying web traffic for Raptor. Currently
limited to record/replay on the GeckoView example app for Android.


## Installation

```
$ pipenv install
```

## Usage

```
$ pipenv run python studio.py --help
```


## Config file
Create config file ex. *config.cfg*

```
certutil=""
url=""
path=""
```

Run using:
```
$ pipenv run python studio.py --config config.cfg --replay
```
Note: 

Config file settings will override the default settings

Command line setting will override the config file settings

# Resources

- [Code](http://github.com/davehunt/raptor-studio)
