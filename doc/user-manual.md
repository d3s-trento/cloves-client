# Cloves Testbed — Python Client User Manual

This document describes how to use the Python client to access the testbed.

## Getting started

Testbed access is currently done with an interface Python script
`iot_testbed_client.py`. You should have received a copy of that in a software
package after creating your testbed account, as well as the testbed
credentials.
If you have not, contact the testbed administrators.

The first thing to do is to ensure you have Python 3.8 or newer and install the
required packages listed in the `requirements.txt` in the testbed software
package.  We tested the scripts with the package versions specified in that file,
but it will probably work also with newer versions.

Next, make the testbed client script memorize your personal testbed access
token so that you don't have to enter it every time you issue a testbed command.
For that, run the following in the testbed software package directory,
replacing `XXXXXX` with your personal token.

```
./iot_testbed_client.py --token XXXXXX saveConfig
```

It will create a hidden file `.iottestbed.config.json` in your home directory
to store the token.

## General workflow

 1. Compile your code targeting one of the supported platforms: `evb1000`, `dwm1001`, `firefly`. Note that only few nodes have the `dwm1001` platform installed.
 2. Prepare a `.json` file describing the job to be run. It sets the desired testbed configuration, binary (or binaries) to load to nodes, and job timing.
 3. Connect to the network of the university with a supported VPN. The testbed server cannot be reached from the outside.
 4. Call the testbed client `iot_testbed_client.py`, providing the `.json` file.
 5. Wait for the job to complete.
 6. Download the logs.

## Compiling the code
Follow instruction of the firmware development package you use (e.g., `Contiki` for `Firefly` or `Contiki-UWB` for `evb1000` and `dwm1001`).

## Creating a job description
We will cover here the simplest configuration that is enough for the vast majority of cases.
The following provides an example that needs to be tweaked depending on the hardware platform and the testbed configuration you need.

```
{
    "name": "Short test name",
    "description" : "Some optional test description",
    "start_time" : "asap",
    "duration" : 60,
    "logs" : 0,
    "binaries": {
        "hardware" : "evb1000",
        "bin_file" : "my_prog.bin",
        "targets" : [2,6]
    }
}
```

For the start time you can write `"asap"` and the testbed will execute the job
at the first time available, or a specific time in the format `"%Y-%m-%d %H:%M"`.
The job `"duration"` is specified in seconds.

The `"logs"` parameter lets you choose the logging configuration. Setting it to `0` means that logs coming from all the devices are merged into a single file `test.log` (this is the recommended setting).

Binaries section can be a single `JSON` object or a list of such objects in the case you need to use different binaries on different nodes.
The `"hardware"` can be `"evb1000"`, `"firefly"` or `"dwm1001"`, and the binary file is specified in `"bin_file"`. Finally,
`"targets"` specifies the set of nodes that this binary should be loaded to. It can be a list of node IDs like in the example
or a zone/group name (check the testbed maps on the website for zone/group names), for example `"disi"`.

Note that the `dwm1001` platform uses `.hex` files instead of `.bin` files for compiled programs.

For the `firefly` platform you also need to specify the program memory address
in the binary description object. Keep it always `"0x00200000"` unless you know what you are doing:
```
    "binaries": {
        "hardware" : "firefly",
        "bin_file" : "my_prog.bin",
        "programAddress": "0x00200000"
        "targets" : [2,6]
    }
```

## Scheduling jobs
To schedule the job, launch the testbed client script from the directory of the `.json` file.
Use the actual path of the script location instead of `/path/to/` and the actual
job description file instead of `my_test.json`.
```
/path/to/iot_testbed_client.py schedule my_test.json
```

If the job is scheduled successfully, it will display the *job ID* for your reference, as well as the time the
job starts and finishes.

## Downloading the results
After the job is finished, you can download its logs using the following command (replacing `job_id` with the actual job ID).
**Note:** a successfully downloaded job log will be automatically deleted from the server.
```
/path/to/iot_testbed_client.py download job_id
```
It might be convenient to download all your completed jobs by simply executing the command without arguments:
```
/path/to/iot_testbed_client.py download
```

You can add `-u` option to the `download` command if you want the log archive to be unzipped automatically:

```
/path/to/iot_testbed_client.py download -u job_id
```

## Cancel a job
If for any reason you have scheduled a job and you don't want it any more you can cancel that scheduling with the
command:
```
/path/to/iot_testbed_client.py cancel job_id
```
The command works also for the already running job, in this case it is sent a signal to the job to stop and the
operation to close it started and eventually the job is completed earlier.
The time reserved for the job will end 30 seconds after the command is
issued.

In addition is possible cancel multiple job specifying multiple job if
(space separated).


## Validate a job

An additional feature is the possibility to just validate locally the
job file. The idea is verify the job configuration on client side like
the correctness of files path. Pass this validation don't guarantee
the job pass the validation on server as there are more and deeper
checks that depends on server configurations.


To validate the job file client side the command is
```
/path/to/iot_testbed_client.py validate jobFile
```

where `jobFile` is the path of a JSON configuration file, it is
possible also use a list of configuration file path space separated to
validate more file with one command.

## Manage reservation

The Cloves testbed permit to reserve itself, during a reservation only
the user that have insert the reservation can submit a job.

The script permit to add, delete or modify a reservation, to have a
general help use the command:
```
/path/to/iot_testbed_client.py reservation --help
```

To add a reservation:
```
/path/to/iot_testbed_client.py reservation add <begin> <end>
```
where `begin` can be in the ISO format `YYYY-mm-ddTHH:MM` or a quoted
string in the format `"YYYY-mm-dd HH:MM"` or `now`. The `end` argument can be
specific moment in the same begin format or a positive time delta in
the format `+N` check the script help for details.


To modify a reservation:
```
/path/to/iot_testbed_client.py reservation mod id [--begin <begin>] [--end end]
```

where `id` is the reservation identifier and `begin` and `end` are how
to modify the reservation. At least one of them must be specified and
their format can be absolute or relative or `now`. Check the script help for
the format.

To delete a reservation:
```
/path/to/iot_testbed_client.py reservation del id
```

where `id` is the reservation identifier.
