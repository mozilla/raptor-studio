[![license](https://img.shields.io/badge/license-MPL%202.0-blue.svg)](https://github.com/davehunt/raptor-studio/blob/master/LICENSE.txt)
[![style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Raptor Studio

A simple command-line tool for recording and replaying web traffic for Raptor.


## Installation

```
$ pipenv install
```

## Usage

```
$ pipenv run python studio.py --help

Usage: studio.py [OPTIONS] [PATH]

Options:
  --app [GeckoViewExample|Firefox|Fenix|Chrome|Refbrow|Fennec]
                                  App type to launch.  [required]
  --binary FILE                   Path to the app to launch. If Android, app
                                  path to APK file to install.
  --proxy [mitm2|mitm4|wpr]       Proxy service to use.  [required]
  --record / --replay
  --certutil FILE                 Path to certutil. Note: only when recording
                                  and only on Android.
  --sites FILE                    JSON file containing the websites
                                  information we want to record. Note: only
                                  when recording.
  --url URL                       Site to load. Note: Only when replaying.
  --config FILE                   Read configuration from FILE.
  --help                          Show this message and exit.


```


## Config file
Create config file; e.g. *config.cfg*

```
certutil=""
url=""
path=""
```

Run using:
```
$ pipenv run python studio.py --config config.cfg --replay
```
Notes:

* Config file settings will override the default settings
* Command-line setting will override the config file settings

# Resources

- [Code](http://github.com/mozilla/raptor-studio)
