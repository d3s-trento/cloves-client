# Cloves testbed
This repository contains a python script to use the Coves testbed.
Purpose of this script is provide the base functionality to use the
testbed as validate a job, schedule a job and download the results.

It offers also other functionality as manage reservations.

For a complete documentation pleas refer to doc folder.

## Quick start

Requirements to use this repository:
 + we strongly suggest to use a virtualenv
 + Python 3.8 
 + python packages listed in `requirements.txt`

### Clone the repository and install the requirements

The following command will copy the repository in `cloves-client`
folder and create a virtualenv with all the required packages.

```bash
$ git clone https://github.com/d3s-trento/cloves-client.git
$ cd cloves-client
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

We later refer to the `cloves-client` folder as `CLOVER_ROOT`

### First setup

After all the software is installed, the script require configure the
credentials to access to access Cloves Testbed.
First connect to the Cloves website, login and copy the token in your
profile page.

Than run those command, substituting `XXXXXX` with your token
```bash
$ cd <CLOVES_ROOT>
$ source venv/bin/activate
$ ./iot_testbed_client.py --token XXXXXX saveConfig
```

### How to use

So after the client is properly configured to use it you can just run

```bash
$ cd <CLOVES_ROOT>
$ source venv/bin/activate
$ ./iot_testbed_client.py --help
```
