# CLOVES Testbed — Python Client User Manual

CLOVES can be accessed through its [web interface](https://research.iottestbed.disi.unitn.it),
or the Python script `iot_testbed_client.py`.
Here we describe how to use the latter.

## Getting started

You should have received a copy of the script in a software
package after creating your testbed account, together with testbed
credentials. If you have not, contact the testbed administrators.

First, check that your Python version is 3.8 or newer.
Then, install the required packages listed in `requirements.txt`
in the testbed software package.
We tested the scripts with the package versions specified in that file,
but we expect it to work with newer versions.

Next, make the client script save your personal access
token so that you don't have to enter it every time you issue a testbed command.
Run the following in the software package directory,
replacing `XXXXXX` with your personal token.

```
./iot_testbed_client.py --token XXXXXX saveConfig
```

This will create a hidden file `.iottestbed.config.json` in your home directory
to store the token.

## General workflow

 1. Compile your code targeting one of the supported platforms: `evb1000`, `dwm1001`, `firefly`. Note that only few nodes have the `dwm1001` platform installed.
 2. Prepare a `.json` file describing the job to be run. It sets the desired testbed configuration, binary (or binaries) to load to nodes, and job timing.
 3. Call the testbed client `iot_testbed_client.py`, providing the `.json` file.
 4. Wait for the job to complete.
 5. Download the logs.

## Compiling the code
Follow the instructions of the firmware development package you use (e.g., `Contiki` for `Firefly` or `Contiki-UWB` for `evb1000` and `dwm1001`).

## Creating a job description
We will cover here the simplest configuration, sufficient for the vast majority of cases.
The following provides an example that needs to be tweaked depending on the hardware platform and the testbed configuration you need.

```
{
    "name": "Short test name",
    "island": "DEPT",
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
in the first available time slot.
You can also provide a specific time in the format `"%Y-%m-%d %H:%M"`.
The job `"duration"` is specified in seconds.

The `"logs"` parameter lets you choose the logging configuration.
Setting it to `0` means that logs coming from all the devices are merged into a single file `job.log` (this is the recommended setting).

The `"binaries"` section can be a single `JSON` object,
or a list of such objects in case you need different binaries on different nodes.
The `"hardware"` can be `"evb1000"`, `"firefly"` or `"dwm1001"`.
The binary file is specified in `"bin_file"`.
Finally, `"targets"` indicates the set of nodes that this binary should be loaded to.
It can be a list of node IDs like in the example
or an area/group name (check the testbed maps on the website for area and group names),
for example `"disi"`.

**Note:** some platforms require specific files or configurations.
The `dwm1001` platform uses `.hex` files instead of `.bin` files for compiled programs.
For the `firefly` platform you need to specify the program memory address
in the binary description object. Always use `"0x00200000"` unless you know what you are doing:

```
    "binaries": {
        "hardware" : "firefly",
        "bin_file" : "my_prog.bin",
        "programAddress": "0x00200000",
        "targets" : [2,6]
    }
```

## Scheduling jobs
To schedule a job, launch the testbed client script from the directory of the `.json` file.
Use the actual path of the script instead of `/path/to/` and the actual
job description file instead of `my_test.json`.

```
/path/to/iot_testbed_client.py schedule my_test.json
```

If the job is scheduled successfully, it will display the *job ID* for your reference, as well as the time the
job starts and ends.

## Downloading the results
After the job ends, you can download its logs using the following command (replacing `job_id` with the actual job ID).

**Note:** a successfully downloaded job log will be automatically deleted from the server.

```
/path/to/iot_testbed_client.py download job_id
```

It might be convenient to download all your completed jobs by simply executing the command without arguments:

```
/path/to/iot_testbed_client.py download
```

You can add the `-u` option to the `download` command if you want the logs archive to be unzipped automatically:

```
/path/to/iot_testbed_client.py download -u job_id
```

## Canceling a job
You can cancel a scheduled job with the command:

```
/path/to/iot_testbed_client.py cancel job_id
```

It is possible to cancel multiple jobs by specifying multiple job IDs, space separated.

The command also works for a job that is already running,
in which case the job is completed earlier.
New job can be scheduled in place of canceled ones,
starting from 30 seconds after the command is issued.

## Validating a job
An additional feature is the possibility to validate the
job file locally, without scheduling on the testbed.
This helps to verify the job configuration, e.g.,
the correctness of file paths.
Note that passing this validation does not guarantee
the job will be accepted by the server.

To do client-side validation of a job file, the command is:

```
/path/to/iot_testbed_client.py validate jobFile
```
where `jobFile` is the path to a JSON configuration file.
It is possible to validate multiple files at once (space separated).

## Manage reservations
The CLOVES testbed allows users to make reservations.
During a reservation, only the user that requested it can submit a job.

Through the script, you can add, delete or modify a reservation.
A general help on how to use the command is provided by:

```
/path/to/iot_testbed_client.py reservation --help
```

To add a reservation:

```
/path/to/iot_testbed_client.py reservation add <begin> <end>
```
where `begin` can be in the ISO format `YYYY-mm-ddTHH:MM`, or a quoted
string in the format `"YYYY-mm-dd HH:MM"`, or `now`.
The `end` argument can be a specific moment in the same format of `begin`,
or a positive time delta in the format `+N`. Check the script help for details.

To modify a reservation:

```
/path/to/iot_testbed_client.py reservation mod id [--begin <begin>] [--end end]
```
where `id` is the reservation identifier. `begin` and `end` are how
to modify the reservation. At least one of them must be specified.
Check the script help for the format.

To delete a reservation:

```
/path/to/iot_testbed_client.py reservation del id
```
where `id` is the reservation identifier.
